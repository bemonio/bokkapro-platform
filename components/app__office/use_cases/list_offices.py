from components.app__office.ports import OfficeRepository
from components.domain__office.entities import Office


def list_offices(
    repository: OfficeRepository,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    sort: str = "created_at",
    order: str = "desc",
) -> tuple[list[Office], int]:
    return repository.list(
        page=page,
        page_size=page_size,
        search=search,
        sort=sort,
        order=order,
    )
