from abc import ABC, abstractmethod

from components.domain__vehicle.entities import Vehicle


class VehicleRepository(ABC):
    @abstractmethod
    def list(
        self,
        page: int,
        page_size: int,
        search: str | None,
        sort: str,
        order: str,
    ) -> tuple[list[Vehicle], int]:
        raise NotImplementedError

    @abstractmethod
    def get(self, vehicle_id: int) -> Vehicle | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_uuid(self, vehicle_uuid: str) -> Vehicle | None:
        raise NotImplementedError

    @abstractmethod
    def create(self, vehicle: Vehicle) -> Vehicle:
        raise NotImplementedError

    @abstractmethod
    def update(self, vehicle: Vehicle) -> Vehicle:
        raise NotImplementedError

    @abstractmethod
    def soft_delete(self, vehicle: Vehicle) -> None:
        raise NotImplementedError
