class VehicleError(Exception):
    """Base vehicle domain error."""


class VehicleNotFoundError(VehicleError):
    """Raised when a vehicle is not found."""
