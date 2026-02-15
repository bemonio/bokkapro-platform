from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from components.api__fastapi.schemas.common.pagination import PaginatedResponse

RouteStatus = Literal["draft", "planned", "in_progress", "completed", "cancelled", "failed"]


class RouteCreate(BaseModel):
    office_id: int = Field(ge=1)
    vehicle_id: int = Field(ge=1)
    service_date: date
    status: RouteStatus = "draft"
    total_tasks: int = Field(default=0, ge=0)
    total_distance_m: int | None = Field(default=None, ge=0)
    total_duration_s: int | None = Field(default=None, ge=0)
    total_load: int | None = Field(default=None, ge=0)


class RouteUpdate(BaseModel):
    office_id: int | None = Field(default=None, ge=1)
    vehicle_id: int | None = Field(default=None, ge=1)
    service_date: date | None = None
    status: RouteStatus | None = None
    total_tasks: int | None = Field(default=None, ge=0)
    total_distance_m: int | None = Field(default=None, ge=0)
    total_duration_s: int | None = Field(default=None, ge=0)
    total_load: int | None = Field(default=None, ge=0)


class RouteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    tenant_id: str | None
    office_uuid: str
    office_name: str | None
    vehicle_uuid: str
    vehicle_name: str | None
    service_date: date
    status: RouteStatus
    total_tasks: int
    total_distance_m: int | None
    total_duration_s: int | None
    total_load: int | None
    created_at: datetime
    updated_at: datetime


RouteListResponse = PaginatedResponse[RouteRead]
