from components.app__route.ports import RouteRepository
from components.domain__route.entities import Route


def get_route(repository: RouteRepository, route_uuid: str | int) -> Route | None:
    return repository.get(route_uuid) if isinstance(route_uuid, int) else repository.get_by_uuid(route_uuid)
