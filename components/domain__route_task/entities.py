from dataclasses import dataclass
from datetime import datetime
from typing import Literal

RouteTaskStatus = Literal["pending", "arrived", "completed", "skipped", "failed"]


@dataclass
class RouteTask:
    id: int | None
    uuid: str
    tenant_id: str | None
    route_uuid: str
    task_uuid: str
    sequence_order: int
    planned_arrival_at: datetime | None
    planned_departure_at: datetime | None
    actual_arrival_at: datetime | None
    actual_departure_at: datetime | None
    status: RouteTaskStatus
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

