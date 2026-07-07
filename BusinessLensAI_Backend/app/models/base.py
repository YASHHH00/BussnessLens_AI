"""
BusinessLens AI — SQLAlchemy Declarative Base + Shared Mixins

All ORM models import `Base` from here.
Mixins provide standard columns without requiring every model to repeat them.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# ------------------------------------------------------------------ #
# Declarative Base
# ------------------------------------------------------------------ #

class Base(DeclarativeBase):
    """Shared declarative base — all ORM models inherit from this."""
    pass


# ------------------------------------------------------------------ #
# Mixins
# ------------------------------------------------------------------ #

class TimestampMixin:
    """
    Adds `created_at` and `updated_at` columns to any model.
    Both are timezone-aware UTC timestamps managed automatically by the DB.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class TenantMixin:
    """
    Adds `organization_id` to any tenant-scoped model.
    The BaseRepository enforces this column on every query — no per-endpoint discipline required.
    """

    organization_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )


def generate_uuid() -> uuid.UUID:
    """Default factory for UUID primary keys."""
    return uuid.uuid4()
