"""Global exception handlers for the API."""
from fastapi import Request
from fastapi.responses import JSONResponse
from .exceptions import TaskNotFoundError, TaskAccessDeniedError, ValidationError


async def task_not_found_handler(request: Request, exc: TaskNotFoundError) -> JSONResponse:
    """Handle TaskNotFoundError exceptions."""
    return JSONResponse(
        status_code=404,
        content={
            "detail": str(exc),
            "error_code": "TASK_NOT_FOUND"
        }
    )


async def task_access_denied_handler(request: Request, exc: TaskAccessDeniedError) -> JSONResponse:
    """Handle TaskAccessDeniedError exceptions."""
    return JSONResponse(
        status_code=403,
        content={
            "detail": str(exc),
            "error_code": "TASK_ACCESS_DENIED"
        }
    )


async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle ValidationError exceptions."""
    content = {
        "detail": str(exc),
        "error_code": "VALIDATION_ERROR"
    }

    if exc.field:
        content["field_errors"] = {exc.field: [str(exc)]}

    return JSONResponse(
        status_code=400,
        content=content
    )
