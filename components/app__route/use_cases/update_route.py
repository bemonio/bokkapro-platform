from bases.platform.time import utc_now
from components.app__route.ports import RouteRepository
from components.domain__route.entities import Route
from components.domain__route.errors import RouteNotFoundError


def update_route(repository: RouteRepository, route_uuid: str | int, **changes) -> Route:
    route = repository.get(route_uuid) if isinstance(route_uuid, int) else repository.get_by_uuid(route_uuid)
    if route is None:
        raise RouteNotFoundError(f"Route {route_uuid} not found")

    for key, value in changes.items():
        if value is not None and hasattr(route, key):
            setattr(route, key, value)

    route.updated_at = utc_now()
    return repository.update(route)
