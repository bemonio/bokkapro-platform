from dataclasses import dataclass
from datetime import datetime


@dataclass
class Office:
    id: int | None
    uuid: str
    tenant_id: str | None
    name: str
    address: str | None
    place_id: str | None
    lat: float | None
    lng: float | None
    storage_capacity: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
