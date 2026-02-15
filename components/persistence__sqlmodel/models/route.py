from datetime import date, datetime
from uuid import uuid4

from sqlmodel import Field, SQLModel

from bases.platform.time import utc_now


class RouteModel(SQLModel, table=True):
    __tablename__ = "routes"

    id: int | None = Field(default=None, primary_key=True)
    uuid: str = Field(default_factory=lambda: str(uuid4()), index=True, unique=True)
    tenant_id: str | None = Field(default=None, index=True)

    office_id: int = Field(foreign_key="offices.id", index=True)
    vehicle_id: int = Field(foreign_key="vehicles.id", index=True)

    service_date: date = Field(index=True)
    status: str = Field(default="draft", index=True)

    total_tasks: int = Field(default=0, ge=0)
    total_distance_m: int | None = Field(default=None, ge=0)
    total_duration_s: int | None = Field(default=None, ge=0)
    total_load: int | None = Field(default=None, ge=0)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    deleted_at: datetime | None = Field(default=None, index=True)
