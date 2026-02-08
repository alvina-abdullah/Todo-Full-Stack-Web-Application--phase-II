"""Create database tables directly."""
import asyncio
from src.database.connection import engine
from src.models.task import Task
from sqlmodel import SQLModel


async def create_tables():
    """Create all database tables."""
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(SQLModel.metadata.create_all)
        print("Tables created successfully!")


if __name__ == "__main__":
    asyncio.run(create_tables())
