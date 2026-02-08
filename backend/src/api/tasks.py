"""Task API endpoints."""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.task import TaskCreate, TaskUpdate, TaskReplace, TaskResponse
from ..services.task_service import TaskService
from .dependencies import get_session, get_current_user_id

router = APIRouter()


@router.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Creates a new task for the authenticated user"
)
async def create_task(
    task_data: TaskCreate,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id)
) -> TaskResponse:
    """
    Create a new task.

    - **title**: Task title (required, 1-200 characters)
    - **description**: Task description (optional, max 2000 characters)

    Returns the created task with ID and timestamps.
    """
    task = await TaskService.create_task(session, user_id, task_data)
    return TaskResponse.model_validate(task)


@router.get(
    "/tasks",
    response_model=List[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="List all tasks",
    description="Retrieves all tasks for the authenticated user"
)
async def list_tasks(
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id)
) -> List[TaskResponse]:
    """
    List all tasks for the authenticated user.

    Returns tasks ordered by creation date (newest first).
    """
    tasks = await TaskService.list_tasks(session, user_id)
    return [TaskResponse.model_validate(task) for task in tasks]


@router.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a specific task",
    description="Retrieves details of a specific task"
)
async def get_task(
    task_id: int,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id)
) -> TaskResponse:
    """
    Get a specific task by ID.

    - **task_id**: ID of the task to retrieve

    Returns 404 if task doesn't exist or 403 if task belongs to another user.
    """
    task = await TaskService.get_task(session, task_id, user_id)
    return TaskResponse.model_validate(task)


@router.put(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Replace a task",
    description="Replaces all fields of an existing task"
)
async def replace_task(
    task_id: int,
    task_data: TaskReplace,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id)
) -> TaskResponse:
    """
    Replace a task (full update).

    All fields must be provided:
    - **title**: Task title (required, 1-200 characters)
    - **description**: Task description (optional, max 2000 characters)
    - **completed**: Task completion status (required)

    Returns 404 if task doesn't exist or 403 if task belongs to another user.
    """
    task = await TaskService.replace_task(session, task_id, user_id, task_data)
    return TaskResponse.model_validate(task)


@router.patch(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a task",
    description="Partially updates a task (only specified fields)"
)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id)
) -> TaskResponse:
    """
    Partially update a task.

    Only provided fields will be updated:
    - **title**: Task title (optional, 1-200 characters)
    - **description**: Task description (optional, max 2000 characters)
    - **completed**: Task completion status (optional)

    Returns 404 if task doesn't exist or 403 if task belongs to another user.
    """
    task = await TaskService.update_task(session, task_id, user_id, task_data)
    return TaskResponse.model_validate(task)


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="Permanently deletes a task"
)
async def delete_task(
    task_id: int,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id)
) -> None:
    """
    Delete a task.

    - **task_id**: ID of the task to delete

    Returns 204 on success, 404 if task doesn't exist, or 403 if task belongs to another user.
    """
    await TaskService.delete_task(session, task_id, user_id)
