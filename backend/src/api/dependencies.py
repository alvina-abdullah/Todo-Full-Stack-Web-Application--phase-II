"""Dependency injection functions for the API."""
from typing import AsyncGenerator
from fastapi import Query
from sqlalchemy.ext.asyncio import AsyncSession
from ..database.connection import async_session_maker


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database session."""
    async with async_session_maker() as session:
        yield session


async def get_current_user_id(user_id: int = Query(..., description="User ID (temporary - will be replaced with JWT token extraction)")) -> int:
    """
    Dependency for getting current user ID.

    NOTE: This is a temporary implementation that accepts user_id as a query parameter.
    In production, this will be replaced with JWT token extraction from the Authorization header.
    """
    return user_id
