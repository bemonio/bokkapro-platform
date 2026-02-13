from bases.platform.time import utc_now
from components.app__office.ports import OfficeRepository
from components.domain__office.entities import Office
from components.domain__office.errors import OfficeNotFoundError


def update_office(
    repository: OfficeRepository,
    office_id: int,
    *,
    name: str | None = None,
    address: str | None = None,
    lat: float | None = None,
    lng: float | None = None,
    storage_capacity: int | None = None,
) -> Office:
    office = repository.get(office_id)
    if office is None:
        raise OfficeNotFoundError(f"Office {office_id} not found")

    if name is not None:
        office.name = name
    if address is not None:
        office.address = address
    if lat is not None:
        office.lat = lat
    if lng is not None:
        office.lng = lng
    if storage_capacity is not None:
        office.storage_capacity = storage_capacity

    office.updated_at = utc_now()
    return repository.update(office)
