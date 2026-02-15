from abc import ABC, abstractmethod

from components.domain__route.entities import Route


class RouteRepository(ABC):
    @abstractmethod
    def list(self, page: int, page_size: int, search: str | None, sort: str, order: str) -> tuple[list[Route], int]:
        raise NotImplementedError

    @abstractmethod
    def get(self, route_id: int) -> Route | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_uuid(self, route_uuid: str) -> Route | None:
        raise NotImplementedError

    @abstractmethod
    def create(self, route: Route) -> Route:
        raise NotImplementedError

    @abstractmethod
    def update(self, route: Route) -> Route:
        raise NotImplementedError

    @abstractmethod
    def soft_delete(self, route: Route) -> None:
        raise NotImplementedError
