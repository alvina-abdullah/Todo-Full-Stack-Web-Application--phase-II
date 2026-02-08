"""Verify database table exists."""
import asyncio
from src.database.connection import engine
from sqlalchemy import text


async def verify_table():
    """Check if tasks table exists."""
    async with engine.connect() as conn:
        result = await conn.execute(text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_name = 'tasks'"
        ))
        tables = result.fetchall()

        if tables:
            print("SUCCESS: 'tasks' table exists in database")

            # Get column information
            result = await conn.execute(text(
                "SELECT column_name, data_type, is_nullable "
                "FROM information_schema.columns "
                "WHERE table_name = 'tasks' "
                "ORDER BY ordinal_position"
            ))
            columns = result.fetchall()

            print("\nTable structure:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]} (nullable: {col[2]})")

            # Get indexes
            result = await conn.execute(text(
                "SELECT indexname, indexdef "
                "FROM pg_indexes "
                "WHERE tablename = 'tasks'"
            ))
            indexes = result.fetchall()

            print("\nIndexes:")
            for idx in indexes:
                print(f"  - {idx[0]}")
        else:
            print("ERROR: 'tasks' table does not exist")


if __name__ == "__main__":
    asyncio.run(verify_table())
