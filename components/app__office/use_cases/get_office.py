from components.app__office.ports import OfficeRepository
from components.domain__office.entities import Office
from components.domain__office.errors import OfficeNotFoundError


def get_office(repository: OfficeRepository, office_id: int) -> Office:
    office = repository.get(office_id)
    if office is None:
        raise OfficeNotFoundError(f"Office {office_id} not found")
    return office
