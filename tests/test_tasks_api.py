from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from bases.platform.db import get_session
from main import app


def _build_client() -> TestClient:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)

    def _session_override() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = _session_override
    return TestClient(app)


def test_task_crud_flow() -> None:
    client = _build_client()

    office_res = client.post("/api/offices", json={"name": "HQ", "address": "Main", "lat": 10.0, "lng": 10.0, "storage_capacity": 10})
    assert office_res.status_code == 201

    office_uuid = office_res.json()["uuid"]
    office_id = client.get(f"/api/offices/{office_uuid}").json().get("id") or 1

    create_res = client.post(
        "/api/tasks",
        json={
            "office_id": office_id,
            "type": "pickup",
            "status": "scheduled",
            "lat": 19.43,
            "lng": -99.13,
            "address": "Calle 1",
            "time_window_start": "2026-01-01T10:00:00",
            "time_window_end": "2026-01-01T11:00:00",
            "service_duration_minutes": 30,
            "load_units": 5,
            "priority": "high",
            "reference": "REF-123",
            "notes": "Tocar puerta",
        },
    )
    assert create_res.status_code == 201, create_res.text
    payload = create_res.json()
    task_uuid = payload["uuid"]
    assert payload["office_uuid"] == office_uuid
    assert payload["type"] == "pickup"

    list_res = client.get("/api/tasks")
    assert list_res.status_code == 200
    assert list_res.json()["meta"]["pagination"]["total"] == 1

    get_res = client.get(f"/api/tasks/{task_uuid}")
    assert get_res.status_code == 200
    assert get_res.json()["reference"] == "REF-123"

    update_res = client.put(f"/api/tasks/{task_uuid}", json={"status": "in_progress", "load_units": 7})
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "in_progress"
    assert update_res.json()["load_units"] == 7

    delete_res = client.delete(f"/api/tasks/{task_uuid}")
    assert delete_res.status_code == 204

    get_deleted_res = client.get(f"/api/tasks/{task_uuid}")
    assert get_deleted_res.status_code == 404

    app.dependency_overrides.clear()
