from components.app__route.ports import RouteRepository
from components.domain__route.entities import Route


def list_routes(repository: RouteRepository, *, page: int, page_size: int, search: str | None, sort: str, order: str) -> tuple[list[Route], int]:
    return repository.list(page=page, page_size=page_size, search=search, sort=sort, order=order)
