from components.app__office.ports import OfficeRepository
from components.domain__office.entities import Office
from components.domain__office.errors import OfficeNotFoundError


def get_office(repository: OfficeRepository, office_uuid: str | int) -> Office:
    office = repository.get(office_uuid) if isinstance(office_uuid, int) else repository.get_by_uuid(office_uuid)
    if office is None:
        raise OfficeNotFoundError(f"Office {office_uuid} not found")
    return office
