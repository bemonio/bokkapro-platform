class OfficeError(Exception):
    """Base office domain error."""


class OfficeNotFoundError(OfficeError):
    """Raised when an office is not found."""
