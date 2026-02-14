from abc import ABC, abstractmethod

from components.domain__office.entities import Office


class OfficeRepository(ABC):
    @abstractmethod
    def list(
        self,
        page: int,
        page_size: int,
        search: str | None,
        sort: str,
        order: str,
    ) -> tuple[list[Office], int]:
        raise NotImplementedError

    @abstractmethod
    def get(self, office_id: int) -> Office | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_uuid(self, office_uuid: str) -> Office | None:
        raise NotImplementedError

    @abstractmethod
    def create(self, office: Office) -> Office:
        raise NotImplementedError

    @abstractmethod
    def update(self, office: Office) -> Office:
        raise NotImplementedError

    @abstractmethod
    def soft_delete(self, office: Office) -> None:
        raise NotImplementedError
