"""
BusinessLens AI — Insight Service

Coordinates KPI / Rule evaluations and calls InsightEngine to produce narrative insights.
"""

from __future__ import annotations

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.base_cache import BaseCacheProvider
from app.engines.insight_engine import InsightEngine
from app.registry.field_registry import BusinessFieldRegistry
from app.schemas.insights import InsightGenerationResponse
from app.services.analytics_service import AnalyticsService


class InsightService:
    def __init__(
        self,
        db: AsyncSession,
        registry: BusinessFieldRegistry,
        ai_provider=None,
        cache: BaseCacheProvider | None = None,
    ) -> None:
        self._analytics_svc = AnalyticsService(db, registry, cache)
        self._engine = InsightEngine(ai_provider=ai_provider, cache=cache)

    async def get_insights(
        self,
        connection_id: UUID,
        organization_id: UUID,
        date_range: str = "Current Period",
    ) -> InsightGenerationResponse:
        kpis = await self._analytics_svc.evaluate_kpis(connection_id, organization_id)
        rules = await self._analytics_svc.evaluate_rules(connection_id, organization_id)

        return await self._engine.generate_insights(
            connection_id=connection_id,
            kpi_results=kpis,
            rule_alerts=rules,
            domain_name="retail",
            date_range=date_range,
        )
