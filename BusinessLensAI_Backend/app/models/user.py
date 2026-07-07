"""
BusinessLens AI — User & Role ORM Models
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, TenantMixin, generate_uuid


# ------------------------------------------------------------------ #
# Role Enum
# ------------------------------------------------------------------ #

class UserRole(str):
    """
    Application roles — controls access to endpoints and data.
    Stored as a VARCHAR string in the DB (not a PG ENUM) for portability.
    """
    EXECUTIVE = "executive"
    BUSINESS_MANAGER = "business_manager"
    BUSINESS_ANALYST = "business_analyst"
    DATA_ANALYST = "data_analyst"
    ADMIN = "admin"


# Valid role values (used for validation)
VALID_ROLES: frozenset[str] = frozenset({
    UserRole.EXECUTIVE,
    UserRole.BUSINESS_MANAGER,
    UserRole.BUSINESS_ANALYST,
    UserRole.DATA_ANALYST,
    UserRole.ADMIN,
})


# ------------------------------------------------------------------ #
# User Model
# ------------------------------------------------------------------ #

class User(Base, TenantMixin, TimestampMixin):
    """
    Platform user.

    Security notes:
    - Password is stored as a bcrypt hash (never plaintext)
    - refresh_token_hash stores a hash of the refresh token for invalidation
    - Lockout: 5 failed attempts → 15-minute lock (configurable)
    - theme_preference: user's preferred UI theme (dark/light/system)
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=generate_uuid,
    )
    email: Mapped[str] = mapped_column(
        String(320),  # RFC 5321 max email length
        unique=True,
        nullable=False,
        index=True,
    )
    hashed_password: Mapped[str] = mapped_column(String(72), nullable=False)
    full_name: Mapped[str] = mapped_column(String(256), nullable=False)

    # Role — stored as VARCHAR for portability across DB dialects
    role: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=UserRole.BUSINESS_ANALYST,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Lockout tracking
    failed_login_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )

    # Refresh token (stored as a hash for invalidation without keeping the raw token)
    refresh_token_hash: Mapped[str | None] = mapped_column(
        String(128), nullable=True, default=None
    )

    # UI theme preference (dark | light | system)
    theme_preference: Mapped[str] = mapped_column(
        String(16), nullable=False, default="system"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    @property
    def is_data_analyst(self) -> bool:
        return self.role == UserRole.DATA_ANALYST

    @property
    def can_access_sql_playground(self) -> bool:
        return self.role in (UserRole.DATA_ANALYST, UserRole.ADMIN)
