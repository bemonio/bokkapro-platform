from components.app__route_task.ports import RouteTaskRepository
from components.domain__route_task.entities import RouteTask


def get_route_task(repository: RouteTaskRepository, route_task_uuid: str) -> RouteTask | None:
    return repository.get_by_uuid(route_task_uuid)
