"""
BusinessLens AI — Analytics Service

Orchestrates semantic queries, KPI evaluations, and business rule checking.
Applies caching on query results.
"""

from __future__ import annotations

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.base_cache import BaseCacheProvider
from app.cache.cache_keys import CacheKeys
from app.connectors.connector_factory import ConnectorFactory
from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.engines.analytics_engine import AnalyticsEngine
from app.engines.kpi_engine import KPIEngine
from app.registry.field_registry import BusinessFieldRegistry
from app.repositories.connection_repository import ConnectionRepository
from app.schemas.analytics import (
    AnalyticsQueryRequest,
    AnalyticsQueryResult,
    KPIEvaluationResult,
    RuleTriggerAlert,
)
from app.semantic.semantic_layer import SemanticLayer


class AnalyticsService:
    def __init__(
        self,
        db: AsyncSession,
        registry: BusinessFieldRegistry,
        cache: BaseCacheProvider | None = None,
    ) -> None:
        self._db = db
        self._registry = registry
        self._cache = cache
        self._conn_repo = ConnectionRepository(db)
        self._semantic_layer = SemanticLayer(db=db, cache=cache)
        self._analytics_engine = AnalyticsEngine(registry)
        self._kpi_engine = KPIEngine(registry, self._analytics_engine)
        self._factory = ConnectorFactory()

    async def execute_query(
        self,
        connection_id: UUID,
        organization_id: UUID,
        request: AnalyticsQueryRequest,
        include_debug_sql: bool = False,
    ) -> AnalyticsQueryResult:
        """Run a metadata-driven query against a connection."""
        conn = await self._conn_repo.get_by_id_or_raise(connection_id, organization_id, "Connection")
        context = await self._semantic_layer.get_context(connection_id, organization_id)

        # Check cache
        if self._cache:
            cache_key = CacheKeys._hash(request.model_dump())
            full_key = f"biz:query:{connection_id}:{cache_key}"
            cached = await self._cache.get(full_key)
            if cached:
                return AnalyticsQueryResult(**cached)

        connector = self._factory.create_from_model(conn)
        result = await self._analytics_engine.execute_query(connector, context, request, include_debug_sql)

        if self._cache:
            cache_key = CacheKeys._hash(request.model_dump())
            full_key = f"biz:query:{connection_id}:{cache_key}"
            await self._cache.set(full_key, result.model_dump(), ttl_seconds=settings.CACHE_TTL_SECONDS)

        return result

    async def evaluate_kpis(
        self,
        connection_id: UUID,
        organization_id: UUID,
    ) -> list[KPIEvaluationResult]:
        """Evaluate all domain KPIs for the active domain plugin."""
        conn = await self._conn_repo.get_by_id_or_raise(connection_id, organization_id, "Connection")
        context = await self._semantic_layer.get_context(connection_id, organization_id)

        # Load retail or active plugin KPIs (from plugin manager metadata or retail fallback)
        from app.plugins.domains.retail.kpis import RETAIL_KPIS
        connector = self._factory.create_from_model(conn)
        return await self._kpi_engine.evaluate_all_kpis(connector, context, RETAIL_KPIS)

    async def evaluate_rules(
        self,
        connection_id: UUID,
        organization_id: UUID,
    ) -> list[RuleTriggerAlert]:
        """Evaluate deterministic business rules and generate anomaly alerts."""
        conn = await self._conn_repo.get_by_id_or_raise(connection_id, organization_id, "Connection")
        context = await self._semantic_layer.get_context(connection_id, organization_id)

        from app.plugins.domains.retail.kpis import RETAIL_KPIS
        from app.plugins.domains.retail.rules import RETAIL_RULES

        connector = self._factory.create_from_model(conn)
        kpis = await self._kpi_engine.evaluate_all_kpis(connector, context, RETAIL_KPIS)
        return await self._kpi_engine.evaluate_rules(connector, context, RETAIL_RULES, kpis)
