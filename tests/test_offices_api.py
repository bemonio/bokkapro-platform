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

    res = client.get("/api/offices?search= HQ  &sort=name&order=asc")
    assert res.status_code == 200
    body = res.json()
    assert body["meta"]["filters"] == {"search": "HQ"}
    assert body["meta"]["sort"] == {"by": "name", "order": "asc"}

    app.dependency_overrides.clear()


def test_offices_api_sort_name_asc() -> None:
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

    for name in ["Zulu", "Alpha", "Bravo"]:
        create_res = client.post(
            "/api/offices",
            json={
                "name": name,
                "address": f"{name} St",
                "lat": 35.0,
                "lng": 139.0,
                "storage_capacity": 10,
            },
        )
        assert create_res.status_code == 201

    sorted_res = client.get("/api/offices?sort=name&order=asc")
    assert sorted_res.status_code == 200
    body = sorted_res.json()
    assert [item["name"] for item in body["data"]] == ["Alpha", "Bravo", "Zulu"]

    app.dependency_overrides.clear()


def test_offices_api_search_multi_field_and_multi_token() -> None:
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

    alpha_create_res = client.post(
        "/api/offices",
        json={
            "name": "North Hub",
            "address": "742 Evergreen Terrace",
            "lat": 35.0,
            "lng": 139.0,
            "storage_capacity": 10,
        },
    )
    assert alpha_create_res.status_code == 201, alpha_create_res.text
    alpha_uuid = alpha_create_res.json()["uuid"]

    beta_create_res = client.post(
        "/api/offices",
        json={
            "name": "South Point",
            "address": "100 Market Street",
            "lat": 35.0,
            "lng": 139.0,
            "storage_capacity": 10,
        },
    )
    assert beta_create_res.status_code == 201, beta_create_res.text

    by_name_res = client.get("/api/offices?search=north")
    assert by_name_res.status_code == 200
    by_name_body = by_name_res.json()
    assert by_name_body["meta"]["pagination"]["total"] == 1
    assert by_name_body["data"][0]["name"] == "North Hub"

    by_address_res = client.get("/api/offices?search=market")
    assert by_address_res.status_code == 200
    by_address_body = by_address_res.json()
    assert by_address_body["meta"]["pagination"]["total"] == 1
    assert by_address_body["data"][0]["name"] == "South Point"

    uuid_substring = alpha_uuid.split("-")[0][2:]
    by_uuid_res = client.get(f"/api/offices?search={uuid_substring}")
    assert by_uuid_res.status_code == 200
    by_uuid_body = by_uuid_res.json()
    assert by_uuid_body["meta"]["pagination"]["total"] == 1
    assert by_uuid_body["data"][0]["uuid"] == alpha_uuid

    multi_token_res = client.get("/api/offices?search= north   terrace ")
    assert multi_token_res.status_code == 200
    multi_token_body = multi_token_res.json()
    assert multi_token_body["meta"]["pagination"]["total"] == 1
    assert multi_token_body["data"][0]["name"] == "North Hub"

    blank_res = client.get("/api/offices?search=   ")
    assert blank_res.status_code == 200
    blank_body = blank_res.json()
    assert blank_body["meta"]["pagination"]["total"] == 2

    app.dependency_overrides.clear()
