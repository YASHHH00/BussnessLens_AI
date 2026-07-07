"""
BusinessLens AI — AuditLog ORM Model
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, generate_uuid


class AuditLog(Base):
    """
    Immutable audit trail for all significant platform operations.

    Records are append-only — never updated or deleted.
    Indexed for efficient queries by org+date and user+action.
    """

    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=generate_uuid,
    )

    # Who performed the action
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False, index=True
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False, index=True
    )

    # What was done
    action: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # What resource was affected
    resource_type: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True
    )

    # Structured metadata about the operation
    details: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    # Network context
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)  # IPv6 max = 45 chars

    # Timestamp (server-side, UTC)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Composite indexes for the two most common query patterns
    __table_args__ = (
        Index("ix_audit_org_created", "organization_id", "created_at"),
        Index("ix_audit_user_action", "user_id", "action"),
    )

    def __repr__(self) -> str:
        return f"<AuditLog action={self.action} user={self.user_id} at={self.created_at}>"
