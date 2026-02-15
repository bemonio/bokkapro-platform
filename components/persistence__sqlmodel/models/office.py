from datetime import datetime
from uuid import uuid4

from sqlmodel import Field, SQLModel

from bases.platform.time import utc_now


class OfficeModel(SQLModel, table=True):
    __tablename__ = "offices"

    id: int | None = Field(default=None, primary_key=True)
    uuid: str = Field(default_factory=lambda: str(uuid4()), index=True, unique=True)
    tenant_id: str | None = Field(default=None, index=True)
    name: str = Field(min_length=2)
    address: str | None = None
    place_id: str | None = Field(default=None, index=True)
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)
    storage_capacity: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    deleted_at: datetime | None = Field(default=None)
