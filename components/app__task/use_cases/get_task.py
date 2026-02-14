from components.app__task.ports import TaskRepository
from components.domain__task.entities import Task


def get_task(repository: TaskRepository, task_uuid: str | int) -> Task | None:
    return repository.get(task_uuid) if isinstance(task_uuid, int) else repository.get_by_uuid(task_uuid)
