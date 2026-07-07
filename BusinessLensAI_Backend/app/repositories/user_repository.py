"""
BusinessLens AI — User Repository
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select, update

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model_class = User

    async def get_by_email(self, email: str) -> User | None:
        """Find a user by email (case-insensitive). Not tenant-scoped (emails are globally unique)."""
        stmt = select(User).where(User.email == email.lower())
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_no_tenant(self, user_id: UUID) -> User | None:
        """Get a user by ID without tenant check (for internal auth operations)."""
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        """Return True if an account with this email exists."""
        user = await self.get_by_email(email)
        return user is not None

    async def increment_failed_attempts(self, user_id: UUID) -> int:
        """Increment failed login counter. Returns the new count."""
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(failed_login_attempts=User.failed_login_attempts + 1)
            .returning(User.failed_login_attempts)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def lock_account(self, user_id: UUID, locked_until) -> None:
        """Set account lockout expiry."""
        await self.db.execute(
            update(User).where(User.id == user_id).values(locked_until=locked_until)
        )

    async def reset_failed_attempts(self, user_id: UUID) -> None:
        """Reset failed attempts and clear lockout after successful login."""
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(failed_login_attempts=0, locked_until=None)
        )

    async def save_refresh_token_hash(self, user_id: UUID, token_hash: str | None) -> None:
        """Persist the refresh token hash (used for invalidation)."""
        await self.db.execute(
            update(User).where(User.id == user_id).values(refresh_token_hash=token_hash)
        )

    async def update_theme_preference(self, user_id: UUID, theme: str) -> None:
        """Update the user's theme preference."""
        await self.db.execute(
            update(User).where(User.id == user_id).values(theme_preference=theme)
        )

    async def deactivate(self, user_id: UUID, organization_id: UUID) -> None:
        """Soft-delete: mark user as inactive."""
        await self.db.execute(
            update(User)
            .where(User.id == user_id, User.organization_id == organization_id)
            .values(is_active=False)
        )
