"""Check what tables exist in the database."""
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

async def check_tables():
    """Check what tables exist in the database."""
    engine = create_async_engine(os.getenv('DATABASE_URL'))

    try:
        async with engine.connect() as conn:
            result = await conn.execute(
                text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema='public' ORDER BY table_name"
                )
            )
            tables = [row[0] for row in result]

            print("Tables in database:")
            for table in tables:
                print(f"  - {table}")

            # Check for Better Auth tables
            auth_tables = [t for t in tables if 'user' in t.lower() or 'session' in t.lower() or 'account' in t.lower()]
            if auth_tables:
                print("\nBetter Auth related tables found:")
                for table in auth_tables:
                    print(f"  - {table}")
            else:
                print("\nNo Better Auth tables found yet.")

    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_tables())
