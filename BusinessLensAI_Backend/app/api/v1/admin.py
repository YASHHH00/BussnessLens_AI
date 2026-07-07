"""
BusinessLens AI — Admin & AI Cost Monitoring API Router
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.api.deps import get_cache, require_role
from app.core.database import get_db
from app.schemas.admin import AICostStatsResponse, SystemHealthResponse
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["Administration"], dependencies=[require_role("admin")])


@router.get("/ai-costs", response_model=list[AICostStatsResponse])
async def get_ai_cost_stats(
    db: AsyncSession = Depends(get_db),
    cache=Depends(get_cache),
):
    """Get AI provider token usage and estimated cost metrics."""
    ai_provider = getattr(deps, "_ai_provider", None)
    svc = AdminService(db=db, ai_provider=ai_provider, cache=cache)
    return await svc.get_ai_stats()


@router.get("/health", response_model=SystemHealthResponse)
async def get_system_health(
    db: AsyncSession = Depends(get_db),
    cache=Depends(get_cache),
):
    """Get system health and database diagnostic metrics."""
    ai_provider = getattr(deps, "_ai_provider", None)
    svc = AdminService(db=db, ai_provider=ai_provider, cache=cache)
    return await svc.get_system_health()
