from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from bases.platform.db import get_session
from main import app


def test_office_crud_flow() -> None:
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

    create_res = client.post(
        "/api/offices",
        json={
            "name": "HQ",
            "address": "1 Main St",
            "lat": 35.0,
            "lng": 139.0,
            "storage_capacity": 10,
        },
    )
    assert create_res.status_code == 201, create_res.text
    office_id = create_res.json()["id"]

    list_res = client.get("/api/offices")
    assert list_res.status_code == 200
    list_body = list_res.json()
    assert list_body["meta"]["pagination"]["total"] == 1
    assert list_body["meta"]["pagination"]["page"] == 1
    assert list_body["meta"]["pagination"]["pageSize"] == 20
    assert list_body["meta"]["pagination"]["pages"] == 1
    assert list_body["meta"]["pagination"]["hasNext"] is False
    assert list_body["meta"]["pagination"]["hasPrev"] is False
    assert list_body["meta"]["filters"] is None
    assert list_body["meta"]["sort"] is None
    assert len(list_body["data"]) == 1

    get_res = client.get(f"/api/offices/{office_id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "HQ"

    update_res = client.put(
        f"/api/offices/{office_id}",
        json={"name": "HQ Updated", "storage_capacity": 20},
    )
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "HQ Updated"
    assert update_res.json()["storage_capacity"] == 20

    delete_res = client.delete(f"/api/offices/{office_id}")
    assert delete_res.status_code == 204

    get_deleted_res = client.get(f"/api/offices/{office_id}")
    assert get_deleted_res.status_code == 404

    list_deleted_res = client.get("/api/offices")
    assert list_deleted_res.status_code == 200
    assert list_deleted_res.json()["meta"]["pagination"]["total"] == 0

    app.dependency_overrides.clear()


def test_office_list_meta_echoes_filters_and_sort() -> None:
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

    res = client.get("/api/offices?search=HQ&sort_by=name&sort_order=asc")
    assert res.status_code == 200
    body = res.json()
    assert body["meta"]["filters"] == {"search": "HQ"}
    assert body["meta"]["sort"] == {"by": "name", "order": "asc"}

    app.dependency_overrides.clear()
