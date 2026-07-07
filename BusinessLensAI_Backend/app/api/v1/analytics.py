"""
BusinessLens AI — Analytics API Router
"""

from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_cache, get_field_registry
from app.core.database import get_db
from app.schemas.analytics import (
    AnalyticsQueryRequest,
    AnalyticsQueryResult,
    KPIEvaluationResult,
    RuleTriggerAlert,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/connections/{connection_id}/analytics", tags=["Analytics Engine"])


@router.post("/query", response_model=AnalyticsQueryResult)
async def run_analytics_query(
    connection_id: UUID,
    request: AnalyticsQueryRequest,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
    registry=Depends(get_field_registry),
    cache=Depends(get_cache),
):
    """
    Execute a semantic query using business field vocabulary.
    Returns rows and columns without exposing physical DB structure.
    Include debug SQL only if user is admin/analyst.
    """
    svc = AnalyticsService(db=db, registry=registry, cache=cache)
    include_sql = current_user.role in ("admin", "data_analyst")
    return await svc.execute_query(connection_id, current_user.organization_id, request, include_debug_sql=include_sql)


@router.get("/kpis", response_model=list[KPIEvaluationResult])
async def evaluate_kpis(
    connection_id: UUID,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
    registry=Depends(get_field_registry),
    cache=Depends(get_cache),
):
    """Evaluate all domain KPIs over the connection's data."""
    svc = AnalyticsService(db=db, registry=registry, cache=cache)
    return await svc.evaluate_kpis(connection_id, current_user.organization_id)


@router.get("/rules", response_model=list[RuleTriggerAlert])
async def evaluate_business_rules(
    connection_id: UUID,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
    registry=Depends(get_field_registry),
    cache=Depends(get_cache),
):
    """Evaluate deterministic business rules / anomaly triggers."""
    svc = AnalyticsService(db=db, registry=registry, cache=cache)
    return await svc.evaluate_rules(connection_id, current_user.organization_id)
