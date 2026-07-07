"""
BusinessLens AI — Async Database Engine & Session Factory

Usage:
    from app.core.database import get_db

    @router.get("/example")
    async def example(db: AsyncSession = Depends(get_db)):
        ...
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

# ------------------------------------------------------------------ #
# Engine (module-level singleton — created once at startup)
# ------------------------------------------------------------------ #
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Return the global async engine, raising if not yet initialized."""
    if _engine is None:
        raise RuntimeError(
            "Database engine has not been initialized. "
            "Call init_db() during app lifespan startup."
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    if _session_factory is None:
        raise RuntimeError(
            "Session factory has not been initialized. "
            "Call init_db() during app lifespan startup."
        )
    return _session_factory


# ------------------------------------------------------------------ #
# Lifecycle helpers (called from app/main.py lifespan)
# ------------------------------------------------------------------ #

def init_db() -> None:
    """
    Create the async engine and session factory.
    Called once during application startup.
    """
    global _engine, _session_factory

    _engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DB_ECHO,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_pre_ping=True,  # Detect stale connections before using them
    )

    _session_factory = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,  # Keep objects usable after commit
        autoflush=False,
        autocommit=False,
    )


async def close_db() -> None:
    """
    Dispose of the async engine connection pool.
    Called once during application shutdown.
    """
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None


# ------------------------------------------------------------------ #
# FastAPI Dependency
# ------------------------------------------------------------------ #

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an async database session.
    Commits on success, rolls back on exception, always closes.

    Usage:
        db: AsyncSession = Depends(get_db)
    """
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ------------------------------------------------------------------ #
# Context manager (for use outside FastAPI — scripts, background tasks)
# ------------------------------------------------------------------ #

@asynccontextmanager
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager for database sessions outside of FastAPI request scope.

    Usage:
        async with db_session() as db:
            result = await db.execute(...)
    """
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
