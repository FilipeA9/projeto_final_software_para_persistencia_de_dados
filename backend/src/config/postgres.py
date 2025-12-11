"""
PostgreSQL database connection and session management.

Provides async SQLAlchemy engine and session factory.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from src.config.settings import settings

# Create async engine
# Convert postgresql:// to postgresql+asyncpg://
database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Add SSL mode to avoid Windows connection issues
if "?" not in database_url:
    database_url += "?ssl=prefer"
else:
    database_url += "&ssl=prefer"

engine = create_async_engine(
    database_url,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,  # Recycle connections after 1 hour
    connect_args={
        "server_settings": {
            "application_name": "turistando_backend",
        },
        "timeout": 30,
    }
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for SQLAlchemy models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database sessions.
    
    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    
    Yields:
        AsyncSession: Database session that is automatically closed after use.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database connection.
    
    Note: Tables should be created using init_database.py script.
    This function only tests the connection.
    """
    try:
        async with engine.connect() as conn:
            # Test connection
            await conn.execute("SELECT 1")
    except Exception as e:
        print(f"Database connection test failed: {e}")
        raise


async def close_db() -> None:
    """Close database engine and cleanup connections."""
    await engine.dispose()
