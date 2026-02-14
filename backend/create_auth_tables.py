"""
Create Better Auth database tables.

This script creates the necessary tables for Better Auth:
- user: stores user accounts
- session: stores user sessions
- account: stores OAuth accounts (if needed)
- verification: stores email verification tokens
"""
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

async def create_better_auth_tables():
    """Create Better Auth tables in the database."""
    engine = create_async_engine(os.getenv('DATABASE_URL'))

    try:
        async with engine.connect() as conn:
            # Create user table
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS "user" (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    email_verified BOOLEAN DEFAULT FALSE,
                    name TEXT,
                    image TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))

            # Create session table
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS session (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
                    expires_at TIMESTAMP NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))

            # Create account table (for OAuth providers)
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS account (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
                    account_id TEXT NOT NULL,
                    provider_id TEXT NOT NULL,
                    access_token TEXT,
                    refresh_token TEXT,
                    id_token TEXT,
                    expires_at TIMESTAMP,
                    password TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(provider_id, account_id)
                )
            """))

            # Create verification table
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS verification (
                    id TEXT PRIMARY KEY,
                    identifier TEXT NOT NULL,
                    value TEXT NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))

            # Commit the changes
            await conn.commit()

            print("Better Auth tables created successfully!")
            print("\nCreated tables:")
            print("  - user")
            print("  - session")
            print("  - account")
            print("  - verification")

    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_better_auth_tables())
