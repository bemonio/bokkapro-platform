from dataclasses import dataclass
from datetime import datetime


@dataclass
class Vehicle:
    id: int | None
    uuid: str
    tenant_id: str | None
    office_id: int
    office_uuid: str | None
    office_name: str | None
    name: str
    plate: str | None
    lat: float | None
    lng: float | None
    max_capacity: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
