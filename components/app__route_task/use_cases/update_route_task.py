from bases.platform.time import utc_now
from components.app__route_task.ports import RouteTaskRepository
from components.domain__route_task.entities import RouteTask
from components.domain__route_task.errors import RouteTaskNotFoundError


def update_route_task(repository: RouteTaskRepository, route_task_uuid: str | int, **changes) -> RouteTask:
    route_task = repository.get(route_task_uuid) if isinstance(route_task_uuid, int) else repository.get_by_uuid(route_task_uuid)
    if route_task is None:
        raise RouteTaskNotFoundError(f"Route task {route_task_uuid} not found")

    for key, value in changes.items():
        if value is not None and hasattr(route_task, key):
            setattr(route_task, key, value)

    route_task.updated_at = utc_now()
    return repository.update(route_task)
