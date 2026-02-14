"""Task service layer for business logic."""
import logging
from typing import List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.task import Task
from ..schemas.task import TaskCreate, TaskUpdate, TaskReplace
from ..api.exceptions import TaskNotFoundError, TaskAccessDeniedError, ValidationError

# Configure logger
logger = logging.getLogger(__name__)


class TaskService:
    """Service class for task operations."""

    @staticmethod
    async def create_task(
        session: AsyncSession,
        user_id: int,
        task_data: TaskCreate
    ) -> Task:
        """
        Create a new task for the user.

        Args:
            session: Database session
            user_id: ID of the user creating the task
            task_data: Task creation data

        Returns:
            Created task

        Raises:
            ValidationError: If validation fails
        """
        logger.info(f"Creating task for user_id={user_id}, title='{task_data.title}'")

        try:
            # Create task instance
            task = Task(
                title=task_data.title,
                description=task_data.description,
                user_id=user_id,
                completed=False,
            )

            # Add to session and commit
            session.add(task)
            await session.commit()
            await session.refresh(task)

            logger.info(f"Task created successfully: task_id={task.id}, user_id={user_id}")
            return task
        except Exception as e:
            logger.error(f"Error creating task for user_id={user_id}: {str(e)}")
            raise

    @staticmethod
    async def list_tasks(
        session: AsyncSession,
        user_id: int
    ) -> List[Task]:
        """
        List all tasks for a user.

        Args:
            session: Database session
            user_id: ID of the user

        Returns:
            List of tasks ordered by created_at DESC
        """
        logger.info(f"Listing tasks for user_id={user_id}")

        try:
            statement = (
                select(Task)
                .where(Task.user_id == user_id)
                .order_by(Task.created_at.desc())
            )
            result = await session.execute(statement)
            tasks = result.scalars().all()

            logger.info(f"Retrieved {len(tasks)} tasks for user_id={user_id}")
            return list(tasks)
        except Exception as e:
            logger.error(f"Error listing tasks for user_id={user_id}: {str(e)}")
            raise

    @staticmethod
    async def get_task(
        session: AsyncSession,
        task_id: int,
        user_id: int
    ) -> Task:
        """
        Get a specific task by ID.

        Args:
            session: Database session
            task_id: ID of the task
            user_id: ID of the requesting user

        Returns:
            Task if found and owned by user

        Raises:
            TaskNotFoundError: If task doesn't exist
            TaskAccessDeniedError: If task belongs to another user
        """
        logger.info(f"Getting task_id={task_id} for user_id={user_id}")

        try:
            statement = select(Task).where(Task.id == task_id)
            result = await session.execute(statement)
            task = result.scalar_one_or_none()

            if not task:
                logger.warning(f"Task not found: task_id={task_id}")
                raise TaskNotFoundError(task_id)

            if task.user_id != user_id:
                logger.warning(f"Access denied: task_id={task_id}, owner={task.user_id}, requester={user_id}")
                raise TaskAccessDeniedError(task_id, user_id)

            logger.info(f"Task retrieved successfully: task_id={task_id}, user_id={user_id}")
            return task
        except (TaskNotFoundError, TaskAccessDeniedError):
            raise
        except Exception as e:
            logger.error(f"Error getting task_id={task_id} for user_id={user_id}: {str(e)}")
            raise

    @staticmethod
    async def replace_task(
        session: AsyncSession,
        task_id: int,
        user_id: int,
        task_data: TaskReplace
    ) -> Task:
        """
        Replace a task (PUT operation).

        Args:
            session: Database session
            task_id: ID of the task
            user_id: ID of the requesting user
            task_data: New task data

        Returns:
            Updated task

        Raises:
            TaskNotFoundError: If task doesn't exist
            TaskAccessDeniedError: If task belongs to another user
        """
        logger.info(f"Replacing task_id={task_id} for user_id={user_id}")

        try:
            # Get existing task with ownership check
            task = await TaskService.get_task(session, task_id, user_id)

            # Update all fields
            task.title = task_data.title
            task.description = task_data.description
            task.completed = task_data.completed
            task.updated_at = datetime.utcnow()

            await session.commit()
            await session.refresh(task)

            logger.info(f"Task replaced successfully: task_id={task_id}, user_id={user_id}")
            return task
        except (TaskNotFoundError, TaskAccessDeniedError):
            raise
        except Exception as e:
            logger.error(f"Error replacing task_id={task_id} for user_id={user_id}: {str(e)}")
            raise

    @staticmethod
    async def update_task(
        session: AsyncSession,
        task_id: int,
        user_id: int,
        task_data: TaskUpdate
    ) -> Task:
        """
        Partially update a task (PATCH operation).

        Args:
            session: Database session
            task_id: ID of the task
            user_id: ID of the requesting user
            task_data: Partial task data

        Returns:
            Updated task

        Raises:
            TaskNotFoundError: If task doesn't exist
            TaskAccessDeniedError: If task belongs to another user
        """
        logger.info(f"Updating task_id={task_id} for user_id={user_id}")

        try:
            # Get existing task with ownership check
            task = await TaskService.get_task(session, task_id, user_id)

            # Update only provided fields
            if task_data.title is not None:
                task.title = task_data.title
            if task_data.description is not None:
                task.description = task_data.description
            if task_data.completed is not None:
                task.completed = task_data.completed

            task.updated_at = datetime.utcnow()

            await session.commit()
            await session.refresh(task)

            logger.info(f"Task updated successfully: task_id={task_id}, user_id={user_id}")
            return task
        except (TaskNotFoundError, TaskAccessDeniedError):
            raise
        except Exception as e:
            logger.error(f"Error updating task_id={task_id} for user_id={user_id}: {str(e)}")
            raise

    @staticmethod
    async def delete_task(
        session: AsyncSession,
        task_id: int,
        user_id: int
    ) -> None:
        """
        Delete a task.

        Args:
            session: Database session
            task_id: ID of the task
            user_id: ID of the requesting user

        Raises:
            TaskNotFoundError: If task doesn't exist
            TaskAccessDeniedError: If task belongs to another user
        """
        logger.info(f"Deleting task_id={task_id} for user_id={user_id}")

        try:
            # Get existing task with ownership check
            task = await TaskService.get_task(session, task_id, user_id)

            # Delete task
            await session.delete(task)
            await session.commit()

            logger.info(f"Task deleted successfully: task_id={task_id}, user_id={user_id}")
        except (TaskNotFoundError, TaskAccessDeniedError):
            raise
        except Exception as e:
            logger.error(f"Error deleting task_id={task_id} for user_id={user_id}: {str(e)}")
            raise
