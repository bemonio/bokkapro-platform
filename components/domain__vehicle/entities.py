from dataclasses import dataclass
from datetime import datetime


@dataclass
class Vehicle:
    id: int | None
    uuid: str
    tenant_id: str | None
    office_id: int
    name: str
    plate: str | None
    max_capacity: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
