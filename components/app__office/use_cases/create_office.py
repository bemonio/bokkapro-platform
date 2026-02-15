from uuid import uuid4

from bases.platform.time import utc_now
from components.app__office.ports import OfficeRepository
from components.domain__office.entities import Office


def create_office(
    repository: OfficeRepository,
    *,
    name: str,
    address: str | None,
    place_id: str | None,
    lat: float | None,
    lng: float | None,
    storage_capacity: int,
    tenant_id: str | None = None,
    uuid: str | None = None,
) -> Office:
    now = utc_now()
    office = Office(
        id=None,
        uuid=uuid or str(uuid4()),
        tenant_id=tenant_id,
        name=name,
        address=address,
        place_id=place_id,
        lat=lat,
        lng=lng,
        storage_capacity=storage_capacity,
        created_at=now,
        updated_at=now,
        deleted_at=None,
    )
    return repository.create(office)
