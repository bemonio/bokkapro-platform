from bases.platform.time import utc_now
from components.app__task.ports import TaskRepository
from components.domain__task.entities import Task
from components.domain__task.errors import TaskNotFoundError


def update_task(repository: TaskRepository, task_uuid: str | int, **changes) -> Task:
    task = repository.get(task_uuid) if isinstance(task_uuid, int) else repository.get_by_uuid(task_uuid)
    if task is None:
        raise TaskNotFoundError(f"Task {task_uuid} not found")

    for key, value in changes.items():
        if value is not None and hasattr(task, key):
            setattr(task, key, value)

    task.updated_at = utc_now()
    return repository.update(task)
