from abc import ABC, abstractmethod

from components.domain__task.entities import Task


class TaskRepository(ABC):
    @abstractmethod
    def list(self, page: int, page_size: int, search: str | None, sort: str, order: str) -> tuple[list[Task], int]:
        raise NotImplementedError

    @abstractmethod
    def get(self, task_id: int) -> Task | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_uuid(self, task_uuid: str) -> Task | None:
        raise NotImplementedError

    @abstractmethod
    def create(self, task: Task) -> Task:
        raise NotImplementedError

    @abstractmethod
    def update(self, task: Task) -> Task:
        raise NotImplementedError

    @abstractmethod
    def soft_delete(self, task: Task) -> None:
        raise NotImplementedError
