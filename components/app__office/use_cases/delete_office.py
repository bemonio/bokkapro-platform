from bases.platform.time import utc_now
from components.app__office.ports import OfficeRepository
from components.domain__office.errors import OfficeNotFoundError


def delete_office(repository: OfficeRepository, office_uuid: str | int) -> None:
    office = repository.get(office_uuid) if isinstance(office_uuid, int) else repository.get_by_uuid(office_uuid)
    if office is None:
        raise OfficeNotFoundError(f"Office {office_uuid} not found")

    now = utc_now()
    office.deleted_at = now
    office.updated_at = now
    repository.soft_delete(office)
