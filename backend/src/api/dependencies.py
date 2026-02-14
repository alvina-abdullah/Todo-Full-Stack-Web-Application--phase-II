"""Dependency injection functions for the API."""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from ..database.connection import async_session_maker


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database session."""
    async with async_session_maker() as session:
        yield session

