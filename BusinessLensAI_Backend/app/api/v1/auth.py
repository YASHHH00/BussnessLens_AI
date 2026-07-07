"""
BusinessLens AI — Auth API Router

Rate-limited endpoints for registration, login, token refresh, and logout.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.middleware import limiter
from app.schemas.auth import LoginRequest, LogoutRequest, RefreshRequest, RegisterRequest, TokenResponse
from app.schemas.common import MessageResponse
from app.services.auth_service import AuthService
from app.api.deps import CurrentUser

router = APIRouter(prefix="/auth", tags=["Auth"])


def _get_ip(request: Request) -> str | None:
    if request.client:
        return request.client.host
    return None


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    data: RegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user account. Returns an access + refresh token pair."""
    return await AuthService(db).register(data, ip_address=_get_ip(request))


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    data: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate with email and password.
    Rate-limited to 5 attempts per minute per IP.
    Accounts are locked for 15 minutes after 5 consecutive failures.
    """
    return await AuthService(db).login(data, ip_address=_get_ip(request))


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    data: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """Exchange a valid refresh token for a new access + refresh token pair (rotation)."""
    return await AuthService(db).refresh(data.refresh_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: CurrentUser,
    data: LogoutRequest,
    db: AsyncSession = Depends(get_db),
):
    """Invalidate the current session by revoking the refresh token."""
    await AuthService(db).logout(
        user_id=current_user.id,
        refresh_token=data.refresh_token,
    )
    return MessageResponse(message="Logged out successfully.")
