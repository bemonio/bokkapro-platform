from abc import ABC, abstractmethod

from components.domain__route_task.entities import RouteTask


class RouteTaskRepository(ABC):
    @abstractmethod
    def list(self, page: int, page_size: int, search: str | None, sort: str, order: str) -> tuple[list[RouteTask], int]:
        raise NotImplementedError

    @abstractmethod
    def get(self, route_task_id: int) -> RouteTask | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_uuid(self, route_task_uuid: str) -> RouteTask | None:
        raise NotImplementedError

    @abstractmethod
    def create(self, route_task: RouteTask) -> RouteTask:
        raise NotImplementedError

    @abstractmethod
    def update(self, route_task: RouteTask) -> RouteTask:
        raise NotImplementedError

    @abstractmethod
    def soft_delete(self, route_task: RouteTask) -> None:
        raise NotImplementedError
