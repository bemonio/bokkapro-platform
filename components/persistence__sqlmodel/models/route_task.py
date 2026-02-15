from datetime import datetime
from uuid import uuid4

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel

from bases.platform.time import utc_now


class RouteTaskModel(SQLModel, table=True):
    __tablename__ = "route_tasks"
    __table_args__ = (
        UniqueConstraint("route_uuid", "sequence_order", name="uq_route_tasks_route_sequence"),
        UniqueConstraint("route_uuid", "task_uuid", name="uq_route_tasks_route_task"),
    )

    id: int | None = Field(default=None, primary_key=True)
    uuid: str = Field(default_factory=lambda: str(uuid4()), index=True, unique=True)
    tenant_id: str | None = Field(default=None, index=True)

    route_uuid: str = Field(foreign_key="routes.uuid", index=True)
    task_uuid: str = Field(foreign_key="tasks.uuid", index=True)

    sequence_order: int = Field(ge=1, index=True)

    planned_arrival_at: datetime | None = Field(default=None)
    planned_departure_at: datetime | None = Field(default=None)
    actual_arrival_at: datetime | None = Field(default=None)
    actual_departure_at: datetime | None = Field(default=None)
    status: str = Field(default="pending", index=True)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    deleted_at: datetime | None = Field(default=None, index=True)
