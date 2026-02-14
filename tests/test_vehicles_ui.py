from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from bases.platform.db import get_session
from components.persistence__sqlmodel.models.office import OfficeModel
from components.persistence__sqlmodel.models.vehicle import VehicleModel
from main import app


def _build_client() -> tuple[TestClient, Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def _session_override() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = _session_override
    return TestClient(app), Session(engine)


def test_vehicles_ui_list_and_i18n() -> None:
    client, session = _build_client()

    office = OfficeModel(name="Centro", address="Calle 1", storage_capacity=10)
    session.add(office)
    session.commit()
    session.refresh(office)

    session.add(VehicleModel(office_id=office.id, name="Camión", plate="XYZ-001", lat=19.43, lng=-99.13, max_capacity=8))
    session.commit()

    res = client.get("/vehicles?lang=es")
    assert res.status_code == 200
    assert "Vehículos" in res.text
    assert "Camión" in res.text
    assert "Oficina" in res.text
    assert "Centro" in res.text
    assert "lang=es" in res.text

    app.dependency_overrides.clear()


def test_vehicle_new_form_uses_async_office_dropdown() -> None:
    client, _ = _build_client()

    res = client.get("/vehicles/new")
    assert res.status_code == 200
    assert 'name="office_uuid"' in res.text
    assert '/api/offices?' in res.text

    app.dependency_overrides.clear()
