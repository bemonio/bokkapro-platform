from uuid import uuid4

from bases.platform.time import utc_now
from components.app__route_task.ports import RouteTaskRepository
from components.domain__route_task.entities import RouteTask, RouteTaskStatus


def create_route_task(
    repository: RouteTaskRepository,
    *,
    route_uuid: str,
    task_uuid: str,
    sequence_order: int,
    planned_arrival_at,
    planned_departure_at,
    actual_arrival_at,
    actual_departure_at,
    status: RouteTaskStatus,
    tenant_id: str | None = None,
    uuid: str | None = None,
) -> RouteTask:
    now = utc_now()
    route_task = RouteTask(
        id=None,
        uuid=uuid or str(uuid4()),
        tenant_id=tenant_id,
        route_uuid=route_uuid,
        task_uuid=task_uuid,
        sequence_order=sequence_order,
        planned_arrival_at=planned_arrival_at,
        planned_departure_at=planned_departure_at,
        actual_arrival_at=actual_arrival_at,
        actual_departure_at=actual_departure_at,
        status=status,
        created_at=now,
        updated_at=now,
        deleted_at=None,
    )
    return repository.create(route_task)
