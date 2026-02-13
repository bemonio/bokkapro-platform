from collections.abc import Mapping
from math import ceil

from pydantic import ValidationError

from components.api__fastapi.schemas.offices.base import OfficeCreate, OfficeUpdate


def build_pagination(page: int, page_size: int, total: int) -> dict[str, int]:
    total_pages = max(1, ceil(total / page_size)) if page_size else 1
    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "has_prev": page > 1,
        "has_next": page < total_pages,
        "prev_page": max(1, page - 1),
        "next_page": min(total_pages, page + 1),
    }


def validation_errors(exc: ValidationError) -> dict[str, str]:
    errors: dict[str, str] = {}
    for error in exc.errors():
        loc = error.get("loc", [])
        field = str(loc[-1]) if loc else "__all__"
        errors[field] = error.get("msg", "Invalid value")
    return errors


def create_from_form(form_data: Mapping[str, str]) -> tuple[OfficeCreate | None, dict[str, str], dict[str, str]]:
    payload = {
        "name": (form_data.get("name") or "").strip(),
        "address": (form_data.get("address") or "").strip() or None,
        "lat": _as_float_or_none(form_data.get("lat")),
        "lng": _as_float_or_none(form_data.get("lng")),
        "storage_capacity": form_data.get("storage_capacity"),
    }

    values = {k: "" if v is None else str(v) for k, v in payload.items()}

    try:
        return OfficeCreate.model_validate(payload), values, {}
    except ValidationError as exc:
        return None, values, validation_errors(exc)


def update_from_form(form_data: Mapping[str, str]) -> tuple[OfficeUpdate | None, dict[str, str], dict[str, str]]:
    payload = {
        "name": (form_data.get("name") or "").strip() or None,
        "address": (form_data.get("address") or "").strip() or None,
        "lat": _as_float_or_none(form_data.get("lat")),
        "lng": _as_float_or_none(form_data.get("lng")),
        "storage_capacity": _as_int_or_none(form_data.get("storage_capacity")),
    }

    values = {
        "name": "" if payload["name"] is None else str(payload["name"]),
        "address": "" if payload["address"] is None else str(payload["address"]),
        "lat": "" if payload["lat"] is None else str(payload["lat"]),
        "lng": "" if payload["lng"] is None else str(payload["lng"]),
        "storage_capacity": "" if payload["storage_capacity"] is None else str(payload["storage_capacity"]),
    }

    try:
        return OfficeUpdate.model_validate(payload), values, {}
    except ValidationError as exc:
        return None, values, validation_errors(exc)


def _as_float_or_none(value: str | None) -> float | None:
    if value is None or value.strip() == "":
        return None
    try:
        return float(value)
    except ValueError:
        return value  # Let pydantic raise validation error


def _as_int_or_none(value: str | None) -> int | None | str:
    if value is None or value.strip() == "":
        return None
    try:
        return int(value)
    except ValueError:
        return value
