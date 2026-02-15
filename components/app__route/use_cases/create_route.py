from datetime import date
from uuid import uuid4

from bases.platform.time import utc_now
from components.app__route.ports import RouteRepository
from components.domain__route.entities import Route, RouteStatus


def create_route(
    repository: RouteRepository,
    *,
    office_id: int,
    vehicle_id: int,
    service_date: date,
    status: RouteStatus,
    total_tasks: int,
    total_distance_m: int | None,
    total_duration_s: int | None,
    total_load: int | None,
    tenant_id: str | None = None,
    uuid: str | None = None,
) -> Route:
    now = utc_now()
    route = Route(
        id=None,
        uuid=uuid or str(uuid4()),
        tenant_id=tenant_id,
        office_id=office_id,
        office_uuid=None,
        office_name=None,
        vehicle_id=vehicle_id,
        vehicle_uuid=None,
        vehicle_name=None,
        service_date=service_date,
        status=status,
        total_tasks=total_tasks,
        total_distance_m=total_distance_m,
        total_duration_s=total_duration_s,
        total_load=total_load,
        created_at=now,
        updated_at=now,
        deleted_at=None,
    )
    return repository.create(route)
