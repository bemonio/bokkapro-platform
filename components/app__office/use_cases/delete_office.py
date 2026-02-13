from bases.platform.time import utc_now
from components.app__office.ports import OfficeRepository
from components.domain__office.errors import OfficeNotFoundError


def delete_office(repository: OfficeRepository, office_id: int) -> None:
    office = repository.get(office_id)
    if office is None:
        raise OfficeNotFoundError(f"Office {office_id} not found")

    now = utc_now()
    office.deleted_at = now
    office.updated_at = now
    repository.soft_delete(office)
