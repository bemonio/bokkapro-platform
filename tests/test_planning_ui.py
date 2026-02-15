from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from bases.platform.db import get_session
from components.persistence__sqlmodel.models.office import OfficeModel
from main import app


def _build_client() -> tuple[TestClient, Session]:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)

    def _session_override() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = _session_override
    return TestClient(app), Session(engine)


def test_planning_page_renders() -> None:
    client, session = _build_client()
    office = OfficeModel(name="Ops Office", storage_capacity=10)
    session.add(office)
    session.commit()

    res = client.get("/planning?lang=en")
    assert res.status_code == 200
    assert "Daily Planning" in res.text
    assert "Generate Routes" in res.text
    assert "Ops Office" in res.text

    app.dependency_overrides.clear()
