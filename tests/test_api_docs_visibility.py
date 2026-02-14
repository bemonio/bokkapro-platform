import importlib
import os
import sys

from fastapi.testclient import TestClient

from bases.platform.config import get_settings


def _load_app(swagger_enabled: bool):
    os.environ["SWAGGER_UI_ENABLED"] = "true" if swagger_enabled else "false"
    get_settings.cache_clear()
    sys.modules.pop("main", None)
    module = importlib.import_module("main")
    return module.app


def test_docs_hidden_by_default():
    app = _load_app(swagger_enabled=False)
    client = TestClient(app)

    docs_response = client.get("/docs")
    redoc_response = client.get("/redoc")
    openapi_response = client.get("/openapi.json")

    assert docs_response.status_code == 404
    assert redoc_response.status_code == 404
    assert openapi_response.status_code == 200


def test_docs_enabled_with_env_flag():
    app = _load_app(swagger_enabled=True)
    client = TestClient(app)

    docs_response = client.get("/docs")
    redoc_response = client.get("/redoc")
    openapi_response = client.get("/openapi.json")

    assert docs_response.status_code == 200
    assert redoc_response.status_code == 200
    assert openapi_response.status_code == 200


def test_ui_routes_not_in_openapi_schema_when_docs_enabled():
    app = _load_app(swagger_enabled=True)
    client = TestClient(app)

    openapi_response = client.get("/openapi.json")

    assert openapi_response.status_code == 200
    paths = openapi_response.json().get("paths", {})
    assert not any(path == "/" or path.startswith("/offices") for path in paths)
    assert "/api/offices" in paths
