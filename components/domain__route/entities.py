from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal

RouteStatus = Literal["draft", "planned", "in_progress", "completed", "cancelled", "failed"]


@dataclass
class Route:
    id: int | None
    uuid: str
    tenant_id: str | None
    office_id: int
    office_uuid: str | None
    office_name: str | None
    vehicle_id: int
    vehicle_uuid: str | None
    vehicle_name: str | None
    service_date: date
    status: RouteStatus
    total_tasks: int
    total_distance_m: int | None
    total_duration_s: int | None
    total_load: int | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
