from collections.abc import Generator
from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from bases.platform.db import get_session
from components.persistence__sqlmodel.models.office import OfficeModel
from components.persistence__sqlmodel.models.route import RouteModel
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


def test_routes_ui_list_and_i18n() -> None:
    client, session = _build_client()

    office = OfficeModel(name="Centro", address="Calle 1", storage_capacity=10)
    session.add(office)
    session.commit()
    session.refresh(office)

    vehicle = VehicleModel(office_id=office.id, name="Unidad 1", max_capacity=100)
    session.add(vehicle)
    session.commit()
    session.refresh(vehicle)

    session.add(RouteModel(office_id=office.id, vehicle_id=vehicle.id, service_date=date(2026, 1, 1), status="planned", total_tasks=3))
    session.commit()

    res = client.get("/routes?lang=es")
    assert res.status_code == 200
    assert "Rutas" in res.text
    assert "Planificada" in res.text
    assert "Centro" in res.text
    assert "Unidad 1" in res.text
    assert "sort=service_date" in res.text
    assert "sort=status" in res.text
    assert "sort=office_id" in res.text
    assert "sort=vehicle_id" in res.text
    assert "sort=total_tasks" in res.text

    app.dependency_overrides.clear()
