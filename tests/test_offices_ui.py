from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from bases.platform.db import get_session
from main import app


def test_offices_ui_crud_and_htmx_partial() -> None:
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
    client = TestClient(app)

    dashboard_res = client.get("/")
    assert dashboard_res.status_code == 200
    assert "Dashboard" in dashboard_res.text

    create_page_res = client.get("/ui/offices/new")
    assert create_page_res.status_code == 200

    create_res = client.post(
        "/ui/offices/new",
        data={
            "name": "Central",
            "address": "100 Main St",
            "lat": "40.0",
            "lng": "-73.0",
            "storage_capacity": "99",
        },
        follow_redirects=False,
    )
    assert create_res.status_code == 303

    list_res = client.get("/ui/offices")
    assert list_res.status_code == 200
    assert "Central" in list_res.text

    search_partial_res = client.get("/ui/offices?search=Central", headers={"HX-Request": "true"})
    assert search_partial_res.status_code == 200
    assert "<table" in search_partial_res.text
    assert "<html" not in search_partial_res.text

    edit_res = client.post(
        "/ui/offices/1/edit",
        data={
            "name": "Central Updated",
            "address": "100 Main St",
            "lat": "40.0",
            "lng": "-73.0",
            "storage_capacity": "100",
        },
        follow_redirects=False,
    )
    assert edit_res.status_code == 303

    view_res = client.get("/ui/offices/1")
    assert view_res.status_code == 200
    assert "Central Updated" in view_res.text
    assert "disabled" in view_res.text

    delete_res = client.post("/ui/offices/1/delete", follow_redirects=False)
    assert delete_res.status_code == 303

    after_delete_res = client.get("/ui/offices")
    assert "No offices found" in after_delete_res.text

    app.dependency_overrides.clear()
