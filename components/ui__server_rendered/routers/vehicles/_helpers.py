from collections.abc import Mapping

from pydantic import ValidationError

from components.api__fastapi.schemas.vehicles.base import VehicleCreate, VehicleUpdate
from components.ui__server_rendered.routers.offices._helpers import build_pagination


__all__ = ["build_pagination", "create_from_form", "update_from_form"]


def validation_errors(exc: ValidationError) -> dict[str, str]:
    errors: dict[str, str] = {}
    for error in exc.errors():
        loc = error.get("loc", [])
        field = str(loc[-1]) if loc else "__all__"
        errors[field] = error.get("msg", "Invalid value")
    return errors


def create_from_form(form_data: Mapping[str, str]) -> tuple[VehicleCreate | None, dict[str, str], dict[str, str]]:
    payload = {
        "office_id": form_data.get("office_id"),
        "name": (form_data.get("name") or "").strip(),
        "plate": (form_data.get("plate") or "").strip() or None,
        "max_capacity": form_data.get("max_capacity"),
    }
    values = {k: "" if v is None else str(v) for k, v in payload.items()}

    try:
        return VehicleCreate.model_validate(payload), values, {}
    except ValidationError as exc:
        return None, values, validation_errors(exc)


def update_from_form(form_data: Mapping[str, str]) -> tuple[VehicleUpdate | None, dict[str, str], dict[str, str]]:
    payload = {
        "office_id": _as_int_or_none(form_data.get("office_id")),
        "name": (form_data.get("name") or "").strip() or None,
        "plate": (form_data.get("plate") or "").strip() or None,
        "max_capacity": _as_int_or_none(form_data.get("max_capacity")),
    }
    values = {
        "office_id": "" if payload["office_id"] is None else str(payload["office_id"]),
        "name": "" if payload["name"] is None else str(payload["name"]),
        "plate": "" if payload["plate"] is None else str(payload["plate"]),
        "max_capacity": "" if payload["max_capacity"] is None else str(payload["max_capacity"]),
    }

    try:
        return VehicleUpdate.model_validate(payload), values, {}
    except ValidationError as exc:
        return None, values, validation_errors(exc)


def _as_int_or_none(value: str | None) -> int | None | str:
    if value is None or value.strip() == "":
        return None
    try:
        return int(value)
    except ValueError:
        return value
