"""
BusinessLens AI — Forecasting API Router
"""

from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_cache, get_field_registry
from app.core.database import get_db
from app.schemas.forecasting import ForecastRequest, ForecastResponse
from app.services.forecasting_service import ForecastingService

router = APIRouter(prefix="/connections/{connection_id}/forecasting", tags=["Forecasting"])


@router.post("", response_model=ForecastResponse)
async def generate_metric_forecast(
    connection_id: UUID,
    request: ForecastRequest,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
    registry=Depends(get_field_registry),
    cache=Depends(get_cache),
):
    """Compute statistical projections and confidence intervals for a time-series metric."""
    svc = ForecastingService(db=db, registry=registry, cache=cache)
    return await svc.generate_forecast(connection_id, current_user.organization_id, request)
