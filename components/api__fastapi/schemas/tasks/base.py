from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from components.api__fastapi.schemas.common.pagination import PaginatedResponse

TaskType = Literal["pickup", "delivery"]
TaskStatus = Literal["pending", "scheduled", "in_progress", "completed", "failed", "cancelled"]
TaskPriority = Literal["low", "normal", "high"]


class TaskCreate(BaseModel):
    office_id: int = Field(ge=1)
    type: TaskType
    status: TaskStatus = "pending"
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)
    address: str | None = None
    time_window_start: datetime | None = None
    time_window_end: datetime | None = None
    service_duration_minutes: int = Field(default=0, ge=0)
    load_units: int = Field(default=0, ge=0)
    priority: TaskPriority = "normal"
    reference: str | None = None
    notes: str | None = None


class TaskUpdate(BaseModel):
    office_id: int | None = Field(default=None, ge=1)
    type: TaskType | None = None
    status: TaskStatus | None = None
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)
    address: str | None = None
    time_window_start: datetime | None = None
    time_window_end: datetime | None = None
    service_duration_minutes: int | None = Field(default=None, ge=0)
    load_units: int | None = Field(default=None, ge=0)
    priority: TaskPriority | None = None
    reference: str | None = None
    notes: str | None = None


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    tenant_id: str | None
    office_uuid: str
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


TaskListResponse = PaginatedResponse[TaskRead]
