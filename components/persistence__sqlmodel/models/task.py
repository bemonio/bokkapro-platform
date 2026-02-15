from datetime import datetime
from uuid import uuid4

from sqlmodel import Field, SQLModel

from bases.platform.time import utc_now


class TaskModel(SQLModel, table=True):
    __tablename__ = "tasks"

    id: int | None = Field(default=None, primary_key=True)
    uuid: str = Field(default_factory=lambda: str(uuid4()), index=True, unique=True)
    tenant_id: str | None = Field(default=None, index=True)

    office_id: int = Field(foreign_key="offices.id", index=True)
    type: str = Field(default="pickup", index=True)
    status: str = Field(default="pending", index=True)

    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)
    address: str | None = Field(default=None)
    place_id: str | None = Field(default=None, index=True)

    time_window_start: datetime | None = Field(default=None)
    time_window_end: datetime | None = Field(default=None)

    service_duration_minutes: int = Field(default=0, ge=0)
    load_units: int = Field(default=0, ge=0)
    priority: str = Field(default="normal", index=True)
    reference: str | None = Field(default=None, index=True)
    notes: str | None = Field(default=None)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    deleted_at: datetime | None = Field(default=None)
