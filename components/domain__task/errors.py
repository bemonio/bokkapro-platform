class TaskError(Exception):
    """Base task domain error."""


class TaskNotFoundError(TaskError):
    """Raised when a task is not found."""
