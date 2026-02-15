from collections.abc import Mapping
from datetime import date

from pydantic import ValidationError

from components.api__fastapi.schemas.routes.base import RouteCreate, RouteUpdate
from components.ui__server_rendered.routers.offices._helpers import build_pagination

__all__ = ["build_pagination", "create_from_form", "update_from_form"]


def validation_errors(exc: ValidationError) -> dict[str, str]:
    errors: dict[str, str] = {}
    for error in exc.errors():
        loc = error.get("loc", [])
        field = str(loc[-1]) if loc else "__all__"
        errors[field] = error.get("msg", "Invalid value")
    return errors


def create_from_form(form_data: Mapping[str, str]) -> tuple[RouteCreate | None, dict[str, str], dict[str, str]]:
    payload = {
        "office_id": form_data.get("office_id"),
        "vehicle_id": form_data.get("vehicle_id"),
        "service_date": _as_date_or_none(form_data.get("service_date")),
        "status": form_data.get("status") or "draft",
        "total_tasks": form_data.get("total_tasks") or 0,
        "total_distance_m": _as_int_or_none(form_data.get("total_distance_m")),
        "total_duration_s": _as_int_or_none(form_data.get("total_duration_s")),
        "total_load": _as_int_or_none(form_data.get("total_load")),
    }
    values = {k: "" if v is None else str(v) for k, v in payload.items()}
    values["office_name"] = form_data.get("office_name") or ""
    values["vehicle_name"] = form_data.get("vehicle_name") or ""
    try:
        return RouteCreate.model_validate(payload), values, {}
    except ValidationError as exc:
        return None, values, validation_errors(exc)


def update_from_form(form_data: Mapping[str, str]) -> tuple[RouteUpdate | None, dict[str, str], dict[str, str]]:
    payload = {
        "office_id": _as_int_or_none(form_data.get("office_id")),
        "vehicle_id": _as_int_or_none(form_data.get("vehicle_id")),
        "service_date": _as_date_or_none(form_data.get("service_date")),
        "status": form_data.get("status") or None,
        "total_tasks": _as_int_or_none(form_data.get("total_tasks")),
        "total_distance_m": _as_int_or_none(form_data.get("total_distance_m")),
        "total_duration_s": _as_int_or_none(form_data.get("total_duration_s")),
        "total_load": _as_int_or_none(form_data.get("total_load")),
    }
    values = {k: "" if v is None else str(v) for k, v in payload.items()}
    values["office_name"] = form_data.get("office_name") or ""
    values["vehicle_name"] = form_data.get("vehicle_name") or ""
    try:
        return RouteUpdate.model_validate(payload), values, {}
    except ValidationError as exc:
        return None, values, validation_errors(exc)


def _as_int_or_none(value: str | None) -> int | None | str:
    if value is None or value.strip() == "":
        return None
    try:
        return int(value)
    except ValueError:
        return value


def _as_date_or_none(value: str | None) -> date | None | str:
    if value is None or value.strip() == "":
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return value
