"""
BusinessLens AI — Alembic env.py

Configured for:
- Async SQLAlchemy (asyncpg driver)
- Auto-generation using all app models
- DATABASE_URL read from settings (not hardcoded)
"""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# Load app settings and models
from app.core.config import settings
from app.models.base import Base

# ---- Import ALL models so Alembic can detect them ---- #
from app.models.user import User          # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401
from app.models.job import BackgroundJob   # noqa: F401
# Phase 2+ models are imported here once created:
# from app.models.connection import Connection  # noqa: F401
# from app.models.mapping import MappingSet, FieldMapping  # noqa: F401
# from app.models.dashboard import Dashboard, Widget  # noqa: F401
# from app.models.forecast import Forecast  # noqa: F401
# from app.models.report import Report  # noqa: F401

# Alembic config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override sqlalchemy.url from our settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (no DB connection needed)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in async 'online' mode."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
