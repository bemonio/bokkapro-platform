from bases.platform.time import utc_now
from components.app__task.ports import TaskRepository
from components.domain__task.errors import TaskNotFoundError


def delete_task(repository: TaskRepository, task_uuid: str | int) -> None:
    task = repository.get(task_uuid) if isinstance(task_uuid, int) else repository.get_by_uuid(task_uuid)
    if task is None:
        raise TaskNotFoundError(f"Task {task_uuid} not found")

    now = utc_now()
    task.deleted_at = now
    task.updated_at = now
    repository.soft_delete(task)
