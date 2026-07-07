"""
BusinessLens AI — Auth Service

Handles: registration, login (with lockout), token refresh, logout.
Every significant operation emits an audit log.
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import AuditAction, emit_audit_log
from app.core.config import settings
from app.core.exceptions import (
    AccountLockedError,
    AuthenticationError,
    ConflictError,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User, VALID_ROLES
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


def _hash_refresh_token(token: str) -> str:
    """Store a SHA-256 hash of the refresh token, not the raw token."""
    return hashlib.sha256(token.encode()).hexdigest()


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = UserRepository(db)
        self._db = db

    async def register(
        self, data: RegisterRequest, ip_address: str | None = None
    ) -> TokenResponse:
        """
        Register a new user.
        - Validates email uniqueness
        - Hashes password with bcrypt
        - Creates user with a unique organization_id (single-org per user in v1)
        - Issues token pair
        """
        if await self._repo.email_exists(data.email):
            raise ConflictError(
                f"An account with email '{data.email}' already exists."
            )

        organization_id = uuid4()  # Each registration creates its own org in v1
        user = User(
            email=data.email.lower(),
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            organization_id=organization_id,
            theme_preference=settings.DASHBOARD_DEFAULT_THEME,
        )
        user = await self._repo.create(user)

        # Issue tokens
        tokens = self._issue_tokens(user)

        # Audit
        await emit_audit_log(
            db=self._db,
            action=AuditAction.USER_REGISTER,
            user_id=user.id,
            organization_id=user.organization_id,
            resource_type="user",
            resource_id=user.id,
            details={"email": user.email, "role": user.role},
            ip_address=ip_address,
        )

        return tokens

    async def login(
        self, data: LoginRequest, ip_address: str | None = None
    ) -> TokenResponse:
        """
        Authenticate a user.
        - Checks lockout before verifying credentials
        - Increments failed attempts on failure
        - Locks account after MAX_FAILED_LOGIN_ATTEMPTS
        - Resets failed attempts on success
        """
        user = await self._repo.get_by_email(data.email)

        if user is None or not user.is_active:
            # Don't reveal whether email exists
            raise AuthenticationError("Invalid email or password.")

        # Lockout check
        if user.locked_until and user.locked_until > datetime.now(UTC):
            raise AccountLockedError(locked_until=user.locked_until.isoformat())

        # Verify password
        if not verify_password(data.password, user.hashed_password):
            new_count = await self._repo.increment_failed_attempts(user.id)

            await emit_audit_log(
                db=self._db,
                action=AuditAction.USER_LOGIN_FAILED,
                user_id=user.id,
                organization_id=user.organization_id,
                resource_type="user",
                resource_id=user.id,
                details={"attempt": new_count},
                ip_address=ip_address,
            )

            if new_count >= settings.MAX_FAILED_LOGIN_ATTEMPTS:
                lockout_until = datetime.now(UTC) + timedelta(
                    minutes=settings.ACCOUNT_LOCKOUT_MINUTES
                )
                await self._repo.lock_account(user.id, lockout_until)
                await emit_audit_log(
                    db=self._db,
                    action=AuditAction.USER_LOCKED,
                    user_id=user.id,
                    organization_id=user.organization_id,
                    resource_type="user",
                    resource_id=user.id,
                    details={"locked_until": lockout_until.isoformat()},
                    ip_address=ip_address,
                )
                raise AccountLockedError(locked_until=lockout_until.isoformat())

            raise AuthenticationError("Invalid email or password.")

        # Success — reset failed attempts, issue tokens
        await self._repo.reset_failed_attempts(user.id)
        tokens = self._issue_tokens(user)

        await emit_audit_log(
            db=self._db,
            action=AuditAction.USER_LOGIN,
            user_id=user.id,
            organization_id=user.organization_id,
            resource_type="user",
            resource_id=user.id,
            ip_address=ip_address,
        )

        return tokens

    async def refresh(self, refresh_token: str) -> TokenResponse:
        """
        Validate a refresh token and issue a new token pair.
        Rotates the refresh token (old token is invalidated).
        """
        from jose import JWTError
        try:
            payload = decode_token(refresh_token)
        except JWTError:
            raise AuthenticationError("Invalid or expired refresh token.")

        if payload.get("type") != "refresh":
            raise AuthenticationError("Token type is not 'refresh'.")

        user_id = UUID(payload["sub"])
        user = await self._repo.get_by_id_no_tenant(user_id)

        if user is None or not user.is_active:
            raise AuthenticationError("User not found or inactive.")

        # Verify token hash matches stored hash
        token_hash = _hash_refresh_token(refresh_token)
        if user.refresh_token_hash != token_hash:
            raise AuthenticationError("Refresh token has been invalidated.")

        return self._issue_tokens(user)

    async def logout(self, user_id: UUID, refresh_token: str | None = None) -> None:
        """Invalidate the refresh token by clearing its hash."""
        user = await self._repo.get_by_id_no_tenant(user_id)
        if user:
            await self._repo.save_refresh_token_hash(user_id, None)
            await emit_audit_log(
                db=self._db,
                action=AuditAction.USER_LOGOUT,
                user_id=user.id,
                organization_id=user.organization_id,
                resource_type="user",
                resource_id=user.id,
            )

    # ------------------------------------------------------------------ #
    # Private helpers
    # ------------------------------------------------------------------ #

    def _issue_tokens(self, user: User) -> TokenResponse:
        """Create access + refresh token pair and persist the refresh hash."""
        access_token = create_access_token(
            user_id=user.id,
            organization_id=user.organization_id,
            role=user.role,
        )
        refresh_token = create_refresh_token(user_id=user.id)

        # Persist hash of refresh token for future invalidation
        import asyncio
        token_hash = _hash_refresh_token(refresh_token)
        # We schedule this as a coroutine to be awaited by the caller context
        # (repo.save_refresh_token_hash is awaited in _issue_tokens_async)

        # Store synchronously via the already-open session
        self._db.add(user)
        user.refresh_token_hash = token_hash

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
