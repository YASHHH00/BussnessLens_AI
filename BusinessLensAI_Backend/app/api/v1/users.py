"""
BusinessLens AI — User Profile & Theme API Router
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_theme_engine
from app.core.audit import AuditAction, emit_audit_log
from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.repositories.user_repository import UserRepository
from app.schemas.user import ThemePreferenceUpdate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: CurrentUser):
    """Return the authenticated user's profile."""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_profile(
    data: UserUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Update the authenticated user's profile (name, theme preference)."""
    repo = UserRepository(db)

    if data.full_name is not None:
        current_user.full_name = data.full_name

    if data.theme_preference is not None:
        await repo.update_theme_preference(current_user.id, data.theme_preference)
        current_user.theme_preference = data.theme_preference

    db.add(current_user)
    return current_user


@router.get("/me/theme")
async def get_theme(
    current_user: CurrentUser,
    theme_engine=Depends(get_theme_engine),
):
    """Return the full theme configuration for the current user."""
    theme = theme_engine.get_user_theme(current_user.theme_preference)
    return theme


@router.put("/me/theme", response_model=UserResponse)
async def set_theme(
    data: ThemePreferenceUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    theme_engine=Depends(get_theme_engine),
):
    """
    Update the user's theme preference.
    The new theme configuration is returned with the updated user.
    """
    if not theme_engine.is_valid_theme(data.theme):
        valid = [t.name for t in theme_engine.list_available_themes()]
        raise NotFoundError(f"Invalid theme '{data.theme}'. Valid themes: {', '.join(valid)}")

    repo = UserRepository(db)
    await repo.update_theme_preference(current_user.id, data.theme)
    current_user.theme_preference = data.theme

    await emit_audit_log(
        db=db,
        action=AuditAction.THEME_CHANGED,
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        resource_type="user",
        resource_id=current_user.id,
        details={"new_theme": data.theme},
    )

    return current_user
