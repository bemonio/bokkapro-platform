from bases.platform.time import utc_now
from components.app__route.ports import RouteRepository
from components.domain__route.errors import RouteNotFoundError


def delete_route(repository: RouteRepository, route_uuid: str | int) -> None:
    route = repository.get(route_uuid) if isinstance(route_uuid, int) else repository.get_by_uuid(route_uuid)
    if route is None:
        raise RouteNotFoundError(f"Route {route_uuid} not found")

    now = utc_now()
    route.deleted_at = now
    route.updated_at = now
    repository.soft_delete(route)
