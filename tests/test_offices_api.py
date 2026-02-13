from collections.abc import Generator
from time import sleep

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from bases.platform.db import get_session
from main import app


def _build_client() -> TestClient:
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
    return TestClient(app)


def test_office_crud_flow() -> None:
    client = _build_client()

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
    assert len(list_body["data"]) == 1
    assert list_body["meta"]["sort"] == {"field": "created_at", "order": "desc"}

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


def test_list_offices_supports_sorting_by_name_asc_and_desc() -> None:
    client = _build_client()

    client.post("/api/offices", json={"name": "Charlie"})
    client.post("/api/offices", json={"name": "Alpha"})
    client.post("/api/offices", json={"name": "Bravo"})

    v1_res = client.get("/api/v1/offices?sort=name&order=asc")
    assert v1_res.status_code == 200
    assert [item["name"] for item in v1_res.json()["data"]] == ["Alpha", "Bravo", "Charlie"]

    asc_res = client.get("/api/offices?sort=name&order=asc")
    assert asc_res.status_code == 200
    assert [item["name"] for item in asc_res.json()["data"]] == ["Alpha", "Bravo", "Charlie"]
    assert asc_res.json()["meta"]["sort"] == {"field": "name", "order": "asc"}

    desc_res = client.get("/api/offices?sort=name&order=desc")
    assert desc_res.status_code == 200
    assert [item["name"] for item in desc_res.json()["data"]] == ["Charlie", "Bravo", "Alpha"]
    assert desc_res.json()["meta"]["sort"] == {"field": "name", "order": "desc"}

    app.dependency_overrides.clear()


def test_list_offices_supports_sorting_by_created_at() -> None:
    client = _build_client()

    client.post("/api/offices", json={"name": "First"})
    sleep(0.01)
    client.post("/api/offices", json={"name": "Second"})
    sleep(0.01)
    client.post("/api/offices", json={"name": "Third"})

    desc_res = client.get("/api/offices?sort=created_at&order=desc")
    assert desc_res.status_code == 200
    assert [item["name"] for item in desc_res.json()["data"]] == ["Third", "Second", "First"]

    asc_res = client.get("/api/offices?sort=created_at&order=asc")
    assert asc_res.status_code == 200
    assert [item["name"] for item in asc_res.json()["data"]] == ["First", "Second", "Third"]

    app.dependency_overrides.clear()


def test_list_offices_returns_400_for_invalid_sort_field() -> None:
    client = _build_client()

    response = client.get("/api/offices?sort=drop_table&order=asc")

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Invalid sort field 'drop_table'. Allowed fields: id, name, created_at, updated_at"
    )

    app.dependency_overrides.clear()
