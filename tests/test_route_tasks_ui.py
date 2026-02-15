from collections.abc import Generator
from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from bases.platform.db import get_session
from components.persistence__sqlmodel.models.office import OfficeModel
from components.persistence__sqlmodel.models.route import RouteModel
from components.persistence__sqlmodel.models.route_task import RouteTaskModel
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


def test_route_tasks_ui_list_and_i18n() -> None:
    client, session = _build_client()

    office = OfficeModel(name="Centro", address="Calle 1", storage_capacity=10)
    session.add(office)
    session.commit()
    session.refresh(office)

    vehicle = VehicleModel(office_id=office.id, name="Unidad 1", max_capacity=100)
    session.add(vehicle)
    session.commit()
    session.refresh(vehicle)

    route = RouteModel(office_id=office.id, vehicle_id=vehicle.id, service_date=date(2026, 1, 1), status="planned", total_tasks=1)
    session.add(route)
    task = TaskModel(office_id=office.id, type="pickup", status="pending", service_duration_minutes=1, load_units=1, priority="normal")
    session.add(task)
    session.commit()
    session.refresh(route)
    session.refresh(task)

    session.add(RouteTaskModel(route_uuid=route.uuid, task_uuid=task.uuid, sequence_order=1, status="pending"))
    session.commit()

    res = client.get("/route-tasks?lang=es")
    assert res.status_code == 200
    assert "Tareas de ruta" in res.text
    assert "Pendiente" in res.text

    app.dependency_overrides.clear()
