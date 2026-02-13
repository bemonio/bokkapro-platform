from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from components.api__fastapi.schemas.common.pagination import PaginatedResponse


class OfficeCreate(BaseModel):
    name: str = Field(min_length=2)
    address: str | None = None
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)
    storage_capacity: int = Field(default=0, ge=0)


class OfficeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2)
    address: str | None = None
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)
    storage_capacity: int | None = Field(default=None, ge=0)


class OfficeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: str
    tenant_id: str | None
    name: str
    address: str | None
    lat: float | None
    lng: float | None
    storage_capacity: int
    created_at: datetime
    updated_at: datetime


OfficeListResponse = PaginatedResponse[OfficeRead]
