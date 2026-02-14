from collections.abc import Generator
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from bases.platform.db import get_session
from components.persistence__sqlmodel.models.office import OfficeModel
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

    create_page_res = client.get("/offices/new")
    assert create_page_res.status_code == 200

    create_res = client.post(
        "/offices/new",
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

    list_res = client.get("/offices")
    assert list_res.status_code == 200
    assert "Central" in list_res.text

    search_partial_res = client.get("/offices?search=Central", headers={"HX-Request": "true"})
    assert search_partial_res.status_code == 200
    assert "<table" in search_partial_res.text
    assert "<html" not in search_partial_res.text

    edit_res = client.post(
        "/offices/1/edit",
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

    view_res = client.get("/offices/1")
    assert view_res.status_code == 200
    assert "Central Updated" in view_res.text
    assert "disabled" in view_res.text

    delete_res = client.post("/offices/1/delete", follow_redirects=False)
    assert delete_res.status_code == 303

    after_delete_res = client.get("/offices")
    assert "No offices found" in after_delete_res.text

    app.dependency_overrides.clear()


def test_offices_ui_list_route_no_redirect_and_query_params_preserved() -> None:
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

    with Session(engine) as session:
        session.add(OfficeModel(name="Alpha", address="Alpha Ave", lat=40.0, lng=-73.0, storage_capacity=10))
        session.add(OfficeModel(name="Beta", address="Beta Ave", lat=40.0, lng=-73.0, storage_capacity=10))
        session.commit()

    canonical_res = client.get(
        "/offices?page=1&page_size=1&search=Alpha",
        headers={"HX-Request": "true"},
        follow_redirects=False,
    )
    assert canonical_res.status_code == 200
    assert "Alpha" in canonical_res.text
    assert "Beta" not in canonical_res.text

    trailing_res = client.get(
        "/offices/?page=1&page_size=1&search=Alpha",
        headers={"HX-Request": "true"},
        follow_redirects=False,
    )
    assert trailing_res.status_code == 200
    assert "Alpha" in trailing_res.text
    assert "Beta" not in trailing_res.text

    app.dependency_overrides.clear()


def test_offices_ui_sorting_behaviour_and_params_preserved() -> None:
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

    now = datetime.now(timezone.utc)
    with Session(engine) as session:
        session.add(
            OfficeModel(
                name="Zulu",
                address="Zulu St",
                lat=40.0,
                lng=-73.0,
                storage_capacity=10,
                created_at=now - timedelta(days=2),
                updated_at=now - timedelta(days=2),
            )
        )
        session.add(
            OfficeModel(
                name="Alpha",
                address="Alpha St",
                lat=40.0,
                lng=-73.0,
                storage_capacity=10,
                created_at=now - timedelta(days=1),
                updated_at=now - timedelta(days=1),
            )
        )
        session.add(
            OfficeModel(
                name="Bravo",
                address="Bravo St",
                lat=40.0,
                lng=-73.0,
                storage_capacity=10,
                created_at=now,
                updated_at=now,
            )
        )
        session.commit()

    default_res = client.get("/offices", headers={"HX-Request": "true"})
    assert default_res.status_code == 200
    assert default_res.text.index("Alpha") < default_res.text.index("Bravo") < default_res.text.index("Zulu")
    assert 'Name<span aria-hidden="true">↑</span>' in default_res.text

    name_asc_res = client.get(
        "/offices?sort=name&order=asc",
        headers={"HX-Request": "true"},
    )
    assert name_asc_res.status_code == 200
    assert name_asc_res.text.index("Alpha") < name_asc_res.text.index("Bravo") < name_asc_res.text.index("Zulu")
    assert 'Name<span aria-hidden="true">↑</span>' in name_asc_res.text

    name_desc_res = client.get(
        "/offices?sort=name&order=desc",
        headers={"HX-Request": "true"},
    )
    assert name_desc_res.status_code == 200
    assert name_desc_res.text.index("Zulu") < name_desc_res.text.index("Bravo") < name_desc_res.text.index("Alpha")
    assert 'Name<span aria-hidden="true">↓</span>' in name_desc_res.text

    address_res = client.get(
        "/offices?sort=address&order=asc",
        headers={"HX-Request": "true"},
    )
    assert address_res.status_code == 200
    assert address_res.text.index("Alpha") < address_res.text.index("Bravo") < address_res.text.index("Zulu")
    assert 'Address<span aria-hidden="true">↑</span>' in address_res.text

    storage_res = client.get(
        "/offices?sort=storage_capacity&order=desc",
        headers={"HX-Request": "true"},
    )
    assert storage_res.status_code == 200
    assert 'Storage<span aria-hidden="true">↓</span>' in storage_res.text
    assert "Created" not in storage_res.text
    assert "Updated" not in storage_res.text

    preserved_params_res = client.get(
        "/offices?search=Alpha&page_size=5&sort=name&order=asc",
        headers={"HX-Request": "true"},
    )
    assert preserved_params_res.status_code == 200
    assert "search=Alpha&sort=name&order=desc" in preserved_params_res.text
    assert "page=1&page_size=5&search=Alpha&sort=name&order=desc" in preserved_params_res.text

    app.dependency_overrides.clear()


def test_offices_ui_search_multi_field_and_phrase() -> None:
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

    with Session(engine) as session:
        north_office = OfficeModel(
            name="North Hub",
            address="742 Evergreen Terrace",
            lat=35.0,
            lng=139.0,
            storage_capacity=10,
        )
        south_office = OfficeModel(
            name="South Point",
            address="100 Market Street",
            lat=35.0,
            lng=139.0,
            storage_capacity=10,
        )
        session.add(north_office)
        session.add(south_office)
        session.commit()
        session.refresh(north_office)

        north_uuid = north_office.uuid

    by_name_res = client.get("/offices?search=north", headers={"HX-Request": "true"})
    assert by_name_res.status_code == 200
    assert "North Hub" in by_name_res.text
    assert "South Point" not in by_name_res.text

    by_address_res = client.get("/offices?search=market", headers={"HX-Request": "true"})
    assert by_address_res.status_code == 200
    assert "South Point" in by_address_res.text
    assert "North Hub" not in by_address_res.text

    uuid_substring = north_uuid.split("-")[0][2:]
    by_uuid_res = client.get(f"/offices?search={uuid_substring}", headers={"HX-Request": "true"})
    assert by_uuid_res.status_code == 200
    assert "North Hub" in by_uuid_res.text
    assert "South Point" not in by_uuid_res.text

    multi_token_res = client.get("/offices?search= evergreen   terrace ", headers={"HX-Request": "true"})
    assert multi_token_res.status_code == 200
    assert "North Hub" in multi_token_res.text
    assert "South Point" not in multi_token_res.text

    blank_res = client.get("/offices?search=   ", headers={"HX-Request": "true"})
    assert blank_res.status_code == 200
    assert "North Hub" in blank_res.text
    assert "South Point" in blank_res.text

    app.dependency_overrides.clear()


def test_ui_i18n_spanish_and_language_selector() -> None:
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

    dashboard_res = client.get("/?lang=es")
    assert dashboard_res.status_code == 200
    assert "Panel" in dashboard_res.text
    assert "Idioma" in dashboard_res.text

    with Session(engine) as session:
        session.add(OfficeModel(name="Centro", address="Calle Uno", lat=19.4, lng=-99.1, storage_capacity=10))
        session.commit()

    offices_res = client.get("/offices?lang=es", headers={"HX-Request": "true"})
    assert offices_res.status_code == 200
    assert "Nombre" in offices_res.text
    assert "Acciones" in offices_res.text
    assert "lang=es" in offices_res.text

    app.dependency_overrides.clear()
