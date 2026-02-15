from collections.abc import Mapping
from datetime import datetime

from pydantic import ValidationError

from components.api__fastapi.schemas.route_tasks.base import RouteTaskCreate, RouteTaskUpdate
from components.ui__server_rendered.routers.offices._helpers import build_pagination

__all__ = ["build_pagination", "create_from_form", "update_from_form"]


def validation_errors(exc: ValidationError) -> dict[str, str]:
    errors: dict[str, str] = {}
    for error in exc.errors():
        loc = error.get("loc", [])
        field = str(loc[-1]) if loc else "__all__"
        errors[field] = error.get("msg", "Invalid value")
    return errors


def create_from_form(form_data: Mapping[str, str]) -> tuple[RouteTaskCreate | None, dict[str, str], dict[str, str]]:
    payload = {
        "route_uuid": (form_data.get("route_uuid") or "").strip(),
        "task_uuid": (form_data.get("task_uuid") or "").strip(),
        "sequence_order": form_data.get("sequence_order"),
        "planned_arrival_at": _as_datetime_or_none(form_data.get("planned_arrival_at")),
        "planned_departure_at": _as_datetime_or_none(form_data.get("planned_departure_at")),
        "actual_arrival_at": _as_datetime_or_none(form_data.get("actual_arrival_at")),
        "actual_departure_at": _as_datetime_or_none(form_data.get("actual_departure_at")),
        "status": form_data.get("status") or "pending",
    }
    values = {k: "" if v is None else str(v) for k, v in payload.items()}
    try:
        return RouteTaskCreate.model_validate(payload), values, {}
    except ValidationError as exc:
        return None, values, validation_errors(exc)


def update_from_form(form_data: Mapping[str, str]) -> tuple[RouteTaskUpdate | None, dict[str, str], dict[str, str]]:
    payload = {
        "route_uuid": (form_data.get("route_uuid") or "").strip() or None,
        "task_uuid": (form_data.get("task_uuid") or "").strip() or None,
        "sequence_order": _as_int_or_none(form_data.get("sequence_order")),
        "planned_arrival_at": _as_datetime_or_none(form_data.get("planned_arrival_at")),
        "planned_departure_at": _as_datetime_or_none(form_data.get("planned_departure_at")),
        "actual_arrival_at": _as_datetime_or_none(form_data.get("actual_arrival_at")),
        "actual_departure_at": _as_datetime_or_none(form_data.get("actual_departure_at")),
        "status": form_data.get("status") or None,
    }
    values = {k: "" if v is None else str(v) for k, v in payload.items()}
    try:
        return RouteTaskUpdate.model_validate(payload), values, {}
    except ValidationError as exc:
        return None, values, validation_errors(exc)


def _as_datetime_or_none(value: str | None):
    if value is None or value.strip() == "":
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return value


def _as_int_or_none(value: str | None) -> int | None | str:
    if value is None or value.strip() == "":
        return None
    try:
        return int(value)
    except ValueError:
        return value
