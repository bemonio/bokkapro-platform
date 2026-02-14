from uuid import uuid4

from bases.platform.time import utc_now
from components.app__task.ports import TaskRepository
from components.domain__task.entities import Task, TaskPriority, TaskStatus, TaskType


def create_task(
    repository: TaskRepository,
    *,
    office_id: int,
    type: TaskType,
    status: TaskStatus,
    lat: float | None,
    lng: float | None,
    address: str | None,
    time_window_start,
    time_window_end,
    service_duration_minutes: int,
    load_units: int,
    priority: TaskPriority,
    reference: str | None,
    notes: str | None,
    tenant_id: str | None = None,
    uuid: str | None = None,
) -> Task:
    now = utc_now()
    task = Task(
        id=None,
        uuid=uuid or str(uuid4()),
        tenant_id=tenant_id,
        office_id=office_id,
        office_uuid=None,
        office_name=None,
        type=type,
        status=status,
        lat=lat,
        lng=lng,
        address=address,
        time_window_start=time_window_start,
        time_window_end=time_window_end,
        service_duration_minutes=service_duration_minutes,
        load_units=load_units,
        priority=priority,
        reference=reference,
        notes=notes,
        created_at=now,
        updated_at=now,
        deleted_at=None,
    )
    return repository.create(task)
