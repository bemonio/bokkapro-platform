from bases.platform.time import utc_now
from components.app__office.ports import OfficeRepository
from components.domain__office.entities import Office
from components.domain__office.errors import OfficeNotFoundError


def update_office(
    repository: OfficeRepository,
    office_uuid: str | int,
    *,
    name: str | None = None,
    address: str | None = None,
    place_id: str | None = None,
    lat: float | None = None,
    lng: float | None = None,
    storage_capacity: int | None = None,
) -> Office:
    office = repository.get(office_uuid) if isinstance(office_uuid, int) else repository.get_by_uuid(office_uuid)
    if office is None:
        raise OfficeNotFoundError(f"Office {office_uuid} not found")

    if name is not None:
        office.name = name
    if address is not None:
        office.address = address
    if place_id is not None:
        office.place_id = place_id
    if lat is not None:
        office.lat = lat
    if lng is not None:
        office.lng = lng
    if storage_capacity is not None:
        office.storage_capacity = storage_capacity

    office.updated_at = utc_now()
    return repository.update(office)
