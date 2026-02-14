from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from components.api__fastapi.schemas.common.pagination import PaginatedResponse


class VehicleCreate(BaseModel):
    office_id: int = Field(ge=1)
    name: str = Field(min_length=2)
    plate: str | None = None
    max_capacity: int = Field(default=0, ge=0)


class VehicleUpdate(BaseModel):
    office_id: int | None = Field(default=None, ge=1)
    name: str | None = Field(default=None, min_length=2)
    plate: str | None = None
    max_capacity: int | None = Field(default=None, ge=0)


class VehicleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    tenant_id: str | None
    office_id: int
    name: str
    plate: str | None
    max_capacity: int
    created_at: datetime
    updated_at: datetime


VehicleListResponse = PaginatedResponse[VehicleRead]
