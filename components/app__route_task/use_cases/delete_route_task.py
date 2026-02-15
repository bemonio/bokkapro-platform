from bases.platform.time import utc_now
from components.app__route_task.ports import RouteTaskRepository
from components.domain__route_task.errors import RouteTaskNotFoundError


def delete_route_task(repository: RouteTaskRepository, route_task_uuid: str | int) -> None:
    route_task = repository.get(route_task_uuid) if isinstance(route_task_uuid, int) else repository.get_by_uuid(route_task_uuid)
    if route_task is None:
        raise RouteTaskNotFoundError(f"Route task {route_task_uuid} not found")

    now = utc_now()
    route_task.deleted_at = now
    route_task.updated_at = now
    repository.soft_delete(route_task)
