from collections.abc import Generator

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


def test_vehicle_crud_flow() -> None:
    client = _build_client()

    office_res = client.post(
        "/api/offices",
        json={"name": "HQ", "address": "Main", "lat": 10.0, "lng": 10.0, "storage_capacity": 10},
    )
    assert office_res.status_code == 201

    office_uuid = office_res.json()["uuid"]
    office_detail_res = client.get(f"/api/offices/{office_uuid}")
    office_id = office_detail_res.json().get("id") or 1

    create_res = client.post(
        "/api/vehicles",
        json={"office_id": office_id, "name": "Truck 1", "plate": "ABC-123", "lat": 19.43, "lng": -99.13, "max_capacity": 12},
    )
    assert create_res.status_code == 201, create_res.text
    vehicle_payload = create_res.json()
    vehicle_uuid = vehicle_payload["uuid"]
    assert "office_id" not in vehicle_payload
    assert vehicle_payload["office_uuid"] == office_uuid
    assert vehicle_payload["office_name"] == "HQ"

    list_res = client.get("/api/vehicles")
    assert list_res.status_code == 200
    assert list_res.json()["meta"]["pagination"]["total"] == 1
    assert list_res.json()["data"][0]["office_name"] == "HQ"

    get_res = client.get(f"/api/vehicles/{vehicle_uuid}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Truck 1"
    assert get_res.json()["lat"] == 19.43

    update_res = client.put(f"/api/vehicles/{vehicle_uuid}", json={"name": "Truck XL", "max_capacity": 20})
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Truck XL"
    assert update_res.json()["max_capacity"] == 20

    delete_res = client.delete(f"/api/vehicles/{vehicle_uuid}")
    assert delete_res.status_code == 204

    get_deleted_res = client.get(f"/api/vehicles/{vehicle_uuid}")
    assert get_deleted_res.status_code == 404

    app.dependency_overrides.clear()
