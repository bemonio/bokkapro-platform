from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from components.api__fastapi.schemas.common.pagination import PaginatedResponse

RouteTaskStatus = Literal["pending", "arrived", "completed", "skipped", "failed"]


class RouteTaskCreate(BaseModel):
    route_uuid: str
    task_uuid: str
    sequence_order: int = Field(ge=1)
    planned_arrival_at: datetime | None = None
    planned_departure_at: datetime | None = None
    actual_arrival_at: datetime | None = None
    actual_departure_at: datetime | None = None
    status: RouteTaskStatus = "pending"


class RouteTaskUpdate(BaseModel):
    route_uuid: str | None = None
    task_uuid: str | None = None
    sequence_order: int | None = Field(default=None, ge=1)
    planned_arrival_at: datetime | None = None
    planned_departure_at: datetime | None = None
    actual_arrival_at: datetime | None = None
    actual_departure_at: datetime | None = None
    status: RouteTaskStatus | None = None


class RouteTaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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


RouteTaskListResponse = PaginatedResponse[RouteTaskRead]
