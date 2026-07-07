"""
BusinessLens AI — Forecasting Service
"""

from __future__ import annotations

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.base_cache import BaseCacheProvider
from app.engines.forecasting_engine import ForecastingEngine
from app.registry.field_registry import BusinessFieldRegistry
from app.schemas.analytics import AnalyticsQueryRequest
from app.schemas.forecasting import ForecastRequest, ForecastResponse
from app.services.analytics_service import AnalyticsService


class ForecastingService:
    def __init__(
        self,
        db: AsyncSession,
        registry: BusinessFieldRegistry,
        cache: BaseCacheProvider | None = None,
    ) -> None:
        self._analytics_svc = AnalyticsService(db, registry, cache)
        self._engine = ForecastingEngine()

    async def generate_forecast(
        self,
        connection_id: UUID,
        organization_id: UUID,
        request: ForecastRequest,
    ) -> ForecastResponse:
        # Run historical query aggregated by date field and time grain
        query_req = AnalyticsQueryRequest(
            metrics=[request.metric_field],
            dimensions=[],
            date_range_field=request.date_field,
            time_grain=request.time_grain,
            order_by=f"{request.date_field} ({request.time_grain})",
            order_direction="asc",
            limit=200,
        )

        res = await self._analytics_svc.execute_query(connection_id, organization_id, query_req)
        return self._engine.compute_forecast(request, res.rows)
