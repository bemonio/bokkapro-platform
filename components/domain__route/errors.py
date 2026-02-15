class RouteError(Exception):
    """Base route domain error."""


class RouteNotFoundError(RouteError):
    """Raised when a route is not found."""
