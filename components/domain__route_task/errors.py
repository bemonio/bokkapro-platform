class RouteTaskError(Exception):
    """Base route-task domain error."""


class RouteTaskNotFoundError(RouteTaskError):
    """Raised when a route-task relation is not found."""

