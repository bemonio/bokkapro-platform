from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from bases.platform.db import get_session
from components.persistence__sqlmodel.models.office import OfficeModel
from components.persistence__sqlmodel.models.task import TaskModel
from main import app


def _build_client() -> tuple[TestClient, Session]:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)

    def _session_override() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = _session_override
    return TestClient(app), Session(engine)


def test_tasks_ui_list_and_i18n() -> None:
    client, session = _build_client()

    office = OfficeModel(name="Centro", address="Calle 1", storage_capacity=10)
    session.add(office)
    session.commit()
    session.refresh(office)

    session.add(TaskModel(office_id=office.id, type="delivery", status="pending", reference="T-001", priority="normal", load_units=3, service_duration_minutes=20))
    session.commit()

    res = client.get("/tasks?lang=es")
    assert res.status_code == 200
    assert "Tareas" in res.text
    assert "Entrega" in res.text
    assert "Centro" in res.text
    assert "lang=es" in res.text

    app.dependency_overrides.clear()


def test_task_view_shows_google_maps_preview() -> None:
    client, session = _build_client()

    office = OfficeModel(name="Centro", address="Calle 1", storage_capacity=10)
    session.add(office)
    session.commit()
    session.refresh(office)

    task = TaskModel(
        office_id=office.id,
        type="delivery",
        status="pending",
        lat=19.43,
        lng=-99.13,
        reference="T-002",
        priority="normal",
        load_units=2,
        service_duration_minutes=15,
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    res = client.get(f"/tasks/{task.id}")
    assert res.status_code == 200
    assert 'x-data="taskMap(\'19.43\', \'-99.13\')"' in res.text
    assert "maps.google.com/maps?q=${encodeURIComponent(lat)},${encodeURIComponent(lng)}" in res.text
    assert "Google map preview" in res.text

    app.dependency_overrides.clear()
