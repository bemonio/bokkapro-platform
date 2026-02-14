from components.app__task.ports import TaskRepository
from components.domain__task.entities import Task


def list_tasks(repository: TaskRepository, *, page: int, page_size: int, search: str | None, sort: str, order: str) -> tuple[list[Task], int]:
    return repository.list(page=page, page_size=page_size, search=search, sort=sort, order=order)
