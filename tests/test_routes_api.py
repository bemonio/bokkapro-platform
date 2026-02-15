from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from bases.platform.db import get_session
from main import app


def _build_client() -> TestClient:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)

    def _session_override() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = _session_override
    return TestClient(app)


def test_route_crud_flow() -> None:
    client = _build_client()

    office = client.post("/api/offices", json={"name": "HQ", "address": "Main", "lat": 10.0, "lng": 10.0, "storage_capacity": 10}).json()
    office_id = client.get(f"/api/offices/{office['uuid']}").json().get("id") or 1

    vehicle = client.post("/api/vehicles", json={"office_id": office_id, "name": "Truck 1", "plate": "ABC-123", "max_capacity": 1000}).json()
    vehicle_id = client.get(f"/api/vehicles/{vehicle['uuid']}").json().get("id") or 1

    create_res = client.post(
        "/api/routes",
        json={
            "office_id": office_id,
            "vehicle_id": vehicle_id,
            "service_date": "2026-01-01",
            "status": "planned",
            "total_tasks": 4,
            "total_distance_m": 12000,
            "total_duration_s": 3600,
            "total_load": 500,
        },
    )
    assert create_res.status_code == 201, create_res.text
    payload = create_res.json()
    route_uuid = payload["uuid"]
    assert payload["office_uuid"] == office["uuid"]
    assert payload["vehicle_uuid"] == vehicle["uuid"]

    list_res = client.get("/api/routes")
    assert list_res.status_code == 200
    assert list_res.json()["meta"]["pagination"]["total"] == 1

    get_res = client.get(f"/api/routes/{route_uuid}")
    assert get_res.status_code == 200
    assert get_res.json()["total_tasks"] == 4

    update_res = client.put(f"/api/routes/{route_uuid}", json={"status": "in_progress", "total_tasks": 5})
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "in_progress"
    assert update_res.json()["total_tasks"] == 5

    delete_res = client.delete(f"/api/routes/{route_uuid}")
    assert delete_res.status_code == 204

    get_deleted_res = client.get(f"/api/routes/{route_uuid}")
    assert get_deleted_res.status_code == 404

    app.dependency_overrides.clear()
