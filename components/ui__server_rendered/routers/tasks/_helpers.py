from collections.abc import Mapping
from datetime import datetime

from pydantic import ValidationError

from components.api__fastapi.schemas.tasks.base import TaskCreate, TaskUpdate
from components.ui__server_rendered.routers.offices._helpers import build_pagination

__all__ = ["build_pagination", "create_from_form", "update_from_form"]


def validation_errors(exc: ValidationError) -> dict[str, str]:
    errors: dict[str, str] = {}
    for error in exc.errors():
        loc = error.get("loc", [])
        field = str(loc[-1]) if loc else "__all__"
        errors[field] = error.get("msg", "Invalid value")
    return errors


def create_from_form(form_data: Mapping[str, str]) -> tuple[TaskCreate | None, dict[str, str], dict[str, str]]:
    payload = {
        "office_id": form_data.get("office_id"),
        "type": form_data.get("type"),
        "status": form_data.get("status") or "pending",
        "lat": _as_float_or_none(form_data.get("lat")),
        "lng": _as_float_or_none(form_data.get("lng")),
        "address": (form_data.get("address") or "").strip() or None,
        "time_window_start": _as_datetime_or_none(form_data.get("time_window_start")),
        "time_window_end": _as_datetime_or_none(form_data.get("time_window_end")),
        "service_duration_minutes": form_data.get("service_duration_minutes"),
        "load_units": form_data.get("load_units"),
        "priority": form_data.get("priority") or "normal",
        "reference": (form_data.get("reference") or "").strip() or None,
        "notes": (form_data.get("notes") or "").strip() or None,
    }
    values = {k: "" if v is None else str(v) for k, v in payload.items()}

    try:
        return TaskCreate.model_validate(payload), values, {}
    except ValidationError as exc:
        return None, values, validation_errors(exc)


def update_from_form(form_data: Mapping[str, str]) -> tuple[TaskUpdate | None, dict[str, str], dict[str, str]]:
    payload = {
        "office_id": _as_int_or_none(form_data.get("office_id")),
        "type": form_data.get("type") or None,
        "status": form_data.get("status") or None,
        "lat": _as_float_or_none(form_data.get("lat")),
        "lng": _as_float_or_none(form_data.get("lng")),
        "address": (form_data.get("address") or "").strip() or None,
        "time_window_start": _as_datetime_or_none(form_data.get("time_window_start")),
        "time_window_end": _as_datetime_or_none(form_data.get("time_window_end")),
        "service_duration_minutes": _as_int_or_none(form_data.get("service_duration_minutes")),
        "load_units": _as_int_or_none(form_data.get("load_units")),
        "priority": form_data.get("priority") or None,
        "reference": (form_data.get("reference") or "").strip() or None,
        "notes": (form_data.get("notes") or "").strip() or None,
    }
    values = {k: "" if v is None else str(v) for k, v in payload.items()}

    try:
        return TaskUpdate.model_validate(payload), values, {}
    except ValidationError as exc:
        return None, values, validation_errors(exc)


def _as_int_or_none(value: str | None) -> int | None | str:
    if value is None or value.strip() == "":
        return None
    try:
        return int(value)
    except ValueError:
        return value


def _as_float_or_none(value: str | None) -> float | None:
    if value is None or value.strip() == "":
        return None
    try:
        return float(value)
    except ValueError:
        return value


def _as_datetime_or_none(value: str | None):
    if value is None or value.strip() == "":
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return value
