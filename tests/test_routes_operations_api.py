from collections.abc import Generator
from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from bases.platform.db import get_session
from components.persistence__sqlmodel.models.office import OfficeModel
from components.persistence__sqlmodel.models.route import RouteModel
from components.persistence__sqlmodel.models.task import TaskModel
from components.persistence__sqlmodel.models.vehicle import VehicleModel
from main import app


def _build_client() -> tuple[TestClient, Session]:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)

    def _session_override() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = _session_override
    return TestClient(app), Session(engine)


def test_generate_and_reorder_route_operations() -> None:
    client, session = _build_client()

    office = OfficeModel(name="Main Office", storage_capacity=100)
    session.add(office)
    session.commit()
    session.refresh(office)

    vehicle = VehicleModel(office_id=office.id, name="Truck 1", max_capacity=50)
    session.add(vehicle)
    session.commit()

    task1 = TaskModel(office_id=office.id, type="delivery", status="pending", load_units=5, address="A", lat=10, lng=20)
    task2 = TaskModel(office_id=office.id, type="pickup", status="pending", load_units=8, address="B", lat=11, lng=21)
    session.add(task1)
    session.add(task2)
    session.commit()

    res = client.post(f"/api/routes/generate?service_date=2026-01-05&office_uuid={office.uuid}")
    assert res.status_code == 200
    assert len(res.json()["data"]) == 1

    route_uuid = res.json()["data"][0]["uuid"]

    detail = client.get(f"/api/routes/{route_uuid}/detail")
    assert detail.status_code == 200
    payload = detail.json()
    assert payload["route"]["total_tasks"] == 2
    assert len(payload["tasks"]) == 2

    ordered = [payload["tasks"][1]["task_uuid"], payload["tasks"][0]["task_uuid"]]
    reorder_res = client.patch(f"/api/routes/{route_uuid}/tasks/reorder", json={"orderedTaskUuids": ordered})
    assert reorder_res.status_code == 200

    detail_after = client.get(f"/api/routes/{route_uuid}/detail")
    assert detail_after.status_code == 200
    assert detail_after.json()["tasks"][0]["task_uuid"] == ordered[0]

    recalc_res = client.post(f"/api/routes/{route_uuid}/recalculate")
    assert recalc_res.status_code == 200

    route = session.exec(select(RouteModel).where(RouteModel.uuid == route_uuid)).first()
    assert route is not None
    assert route.total_load == 13

    app.dependency_overrides.clear()
