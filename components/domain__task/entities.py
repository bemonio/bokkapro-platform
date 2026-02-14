from dataclasses import dataclass
from datetime import datetime
from typing import Literal

TaskType = Literal["pickup", "delivery"]
TaskStatus = Literal["pending", "scheduled", "in_progress", "completed", "failed", "cancelled"]
TaskPriority = Literal["low", "normal", "high"]


@dataclass
class Task:
    id: int | None
    uuid: str
    tenant_id: str | None
    office_id: int
    office_uuid: str | None
    office_name: str | None
    type: TaskType
    status: TaskStatus
    lat: float | None
    lng: float | None
    address: str | None
    time_window_start: datetime | None
    time_window_end: datetime | None
    service_duration_minutes: int
    load_units: int
    priority: TaskPriority
    reference: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
