from components.app__route_task.ports import RouteTaskRepository
from components.domain__route_task.entities import RouteTask


def list_route_tasks(
    repository: RouteTaskRepository,
    *,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    sort: str = "created_at",
    order: str = "desc",
) -> tuple[list[RouteTask], int]:
    return repository.list(page=page, page_size=page_size, search=search, sort=sort, order=order)
