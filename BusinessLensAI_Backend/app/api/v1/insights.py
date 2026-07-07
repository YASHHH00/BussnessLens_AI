"""
BusinessLens AI — AI Insights API Router
"""

from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.api.deps import CurrentUser, get_cache, get_field_registry
from app.core.database import get_db
from app.schemas.insights import InsightGenerationResponse
from app.services.insight_service import InsightService

router = APIRouter(prefix="/connections/{connection_id}/insights", tags=["AI Insights"])


@router.get("", response_model=InsightGenerationResponse)
async def get_ai_insights(
    connection_id: UUID,
    date_range: str = "Current Period",
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
    registry=Depends(get_field_registry),
    cache=Depends(get_cache),
):
    """Generate or retrieve AI-synthesized executive narrative insights and alerts."""
    ai_provider = getattr(deps, "_ai_provider", None)
    svc = InsightService(db=db, registry=registry, ai_provider=ai_provider, cache=cache)
    return await svc.get_insights(connection_id, current_user.organization_id, date_range)
