from collections.abc import Generator
from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from bases.platform.db import get_session
from components.persistence__sqlmodel.models.office import OfficeModel
from components.persistence__sqlmodel.models.route import RouteModel
from components.persistence__sqlmodel.models.task import TaskModel
from components.persistence__sqlmodel.models.vehicle import VehicleModel
from main import app


def _build_client() -> TestClient:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)

    def _session_override() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = _session_override
    return TestClient(app)


def test_route_task_crud_and_constraints() -> None:
    client = _build_client()

    office = client.post("/api/offices", json={"name": "HQ", "address": "Main", "lat": 10.0, "lng": 10.0, "storage_capacity": 10}).json()
    office_id = client.get(f"/api/offices/{office['uuid']}").json().get("id") or 1

    vehicle = client.post("/api/vehicles", json={"office_id": office_id, "name": "Truck 1", "plate": "ABC-123", "max_capacity": 1000}).json()
    vehicle_id = client.get(f"/api/vehicles/{vehicle['uuid']}").json().get("id") or 1

    route = client.post("/api/routes", json={"office_id": office_id, "vehicle_id": vehicle_id, "service_date": "2026-01-01", "status": "planned", "total_tasks": 2, "total_distance_m": 12000, "total_duration_s": 3600, "total_load": 500}).json()

    task = client.post("/api/tasks", json={"office_id": office_id, "type": "pickup", "status": "pending", "service_duration_minutes": 5, "load_units": 3, "priority": "normal"}).json()

    create_res = client.post("/api/route-tasks", json={"route_uuid": route["uuid"], "task_uuid": task["uuid"], "sequence_order": 1, "status": "pending"})
    assert create_res.status_code == 201, create_res.text
    rt_uuid = create_res.json()["uuid"]

    duplicated_sequence = client.post("/api/route-tasks", json={"route_uuid": route["uuid"], "task_uuid": task["uuid"], "sequence_order": 1, "status": "pending"})
    assert duplicated_sequence.status_code == 422

    list_res = client.get("/api/route-tasks")
    assert list_res.status_code == 200
    assert list_res.json()["meta"]["pagination"]["total"] == 1

    get_res = client.get(f"/api/route-tasks/{rt_uuid}")
    assert get_res.status_code == 200

    update_res = client.put(f"/api/route-tasks/{rt_uuid}", json={"status": "arrived"})
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "arrived"

    delete_res = client.delete(f"/api/route-tasks/{rt_uuid}")
    assert delete_res.status_code == 204

    get_deleted_res = client.get(f"/api/route-tasks/{rt_uuid}")
    assert get_deleted_res.status_code == 404

    app.dependency_overrides.clear()
