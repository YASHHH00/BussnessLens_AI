"""
BusinessLens AI — FastAPI Shared Dependencies

All protected routes use these dependencies via FastAPI Depends().
Provides: authenticated user, role checking, registry, plugin, cache, theme engine.
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.security import decode_token
from app.models.user import User, UserRole

security = HTTPBearer(auto_error=False)


# ------------------------------------------------------------------ #
# Application singletons (set at startup from main.py lifespan)
# ------------------------------------------------------------------ #

_field_registry = None
_active_plugin = None
_cache_provider = None
_theme_engine = None
_plugin_manager = None
_ai_provider = None


def set_singletons(registry, plugin, cache, theme, plugin_manager, ai_provider=None) -> None:
    """Called from app lifespan to inject singletons into the deps module."""
    global _field_registry, _active_plugin, _cache_provider, _theme_engine, _plugin_manager, _ai_provider
    _field_registry = registry
    _active_plugin = plugin
    _cache_provider = cache
    _theme_engine = theme
    _plugin_manager = plugin_manager
    _ai_provider = ai_provider


# ------------------------------------------------------------------ #
# Auth dependencies
# ------------------------------------------------------------------ #

async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Decode the Bearer token and return the authenticated User.
    Raises 401 on missing, expired, or invalid tokens.
    Raises 401 if the user is inactive or not found.
    """
    if credentials is None:
        raise AuthenticationError("Authorization header is required.")

    try:
        payload = decode_token(credentials.credentials)
    except JWTError:
        raise AuthenticationError("Invalid or expired access token.")

    if payload.get("type") != "access":
        raise AuthenticationError("Token type must be 'access'.")

    user_id = UUID(payload["sub"])

    from app.repositories.user_repository import UserRepository
    user = await UserRepository(db).get_by_id_no_tenant(user_id)

    if user is None or not user.is_active:
        raise AuthenticationError("User not found or account is inactive.")

    return user


# Typed alias for cleaner function signatures
CurrentUser = Annotated[User, Depends(get_current_user)]


def require_role(*allowed_roles: str):
    """
    Returns a FastAPI dependency that enforces role-based access.

    Usage:
        @router.get("/admin/users", dependencies=[Depends(require_role("admin"))])
        async def list_users(user: CurrentUser): ...
    """
    def _check(user: CurrentUser) -> User:
        if user.role not in allowed_roles:
            raise AuthorizationError(
                f"This endpoint requires one of these roles: {', '.join(allowed_roles)}. "
                f"Your role is: {user.role}."
            )
        return user

    return Depends(_check)


# ------------------------------------------------------------------ #
# Application singleton dependencies
# ------------------------------------------------------------------ #

def get_field_registry():
    """Returns the initialized BusinessFieldRegistry."""
    if _field_registry is None:
        raise RuntimeError("Field registry not initialized.")
    return _field_registry


def get_active_plugin():
    """Returns the loaded domain plugin."""
    if _active_plugin is None:
        raise RuntimeError("Domain plugin not initialized.")
    return _active_plugin


def get_cache():
    """Returns the initialized cache provider."""
    if _cache_provider is None:
        raise RuntimeError("Cache provider not initialized.")
    return _cache_provider


def get_theme_engine():
    """Returns the ThemeEngine instance."""
    if _theme_engine is None:
        raise RuntimeError("Theme engine not initialized.")
    return _theme_engine
