"""Custom exception classes for the API."""


class TaskNotFoundError(Exception):
    """Raised when a task is not found."""

    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f"Task with id {task_id} not found")


class TaskAccessDeniedError(Exception):
    """Raised when a user tries to access a task they don't own."""

    def __init__(self, task_id: int, user_id: int):
        self.task_id = task_id
        self.user_id = user_id
        super().__init__(f"Access denied to task {task_id} for user {user_id}")


class ValidationError(Exception):
    """Raised when input validation fails."""

    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(message)
