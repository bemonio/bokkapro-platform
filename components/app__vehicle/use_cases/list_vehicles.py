from components.app__vehicle.ports import VehicleRepository
from components.domain__vehicle.entities import Vehicle


def list_vehicles(
    repository: VehicleRepository,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    sort: str = "created_at",
    order: str = "desc",
) -> tuple[list[Vehicle], int]:
    return repository.list(
        page=page,
        page_size=page_size,
        search=search,
        sort=sort,
        order=order,
    )
