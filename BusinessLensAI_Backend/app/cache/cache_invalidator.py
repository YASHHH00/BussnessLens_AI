"""
BusinessLens AI — Cache Invalidator

Automatically invalidates stale cache entries when mappings or schema change.
Called by MappingService, SchemaDetectionService, and DashboardService.
"""

from __future__ import annotations

from uuid import UUID

from app.cache.base_cache import BaseCacheProvider
from app.cache.cache_keys import CacheKeys
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class CacheInvalidator:
    """
    Centralized cache invalidation logic.
    Ensures stale data is flushed atomically when the underlying data changes.
    """

    def __init__(self, cache: BaseCacheProvider) -> None:
        self._cache = cache

    async def on_mapping_changed(self, connection_id: UUID) -> None:
        """
        Invalidate ALL cached data for a connection when mappings change.
        Called by: MappingService.save_mappings()

        Rationale: any cached KPI, dashboard query, recommendation, or
        semantic context is now stale because the field-to-column mapping changed.
        """
        pattern = CacheKeys.connection_pattern(connection_id)
        deleted = await self._cache.delete_pattern(pattern)
        logger.info(
            "Cache invalidated on mapping change: connection=%s, keys_deleted=%d",
            connection_id, deleted,
        )

    async def on_schema_changed(self, connection_id: UUID) -> None:
        """
        Invalidate schema-dependent caches when a new schema scan completes.
        Called by: SchemaDetectionService.complete_scan()
        """
        pattern = CacheKeys.connection_pattern(connection_id)
        deleted = await self._cache.delete_pattern(pattern)
        logger.info(
            "Cache invalidated on schema change: connection=%s, keys_deleted=%d",
            connection_id, deleted,
        )

    async def on_dashboard_updated(self, connection_id: UUID, dashboard_id: UUID) -> None:
        """
        Invalidate cached dashboard queries when a dashboard is updated.
        Called by: DashboardService.update_dashboard()
        """
        # Invalidate the specific dashboard's query cache
        pattern = CacheKeys.dashboard_pattern(dashboard_id)
        deleted_dash = await self._cache.delete_pattern(pattern)
        logger.debug(
            "Cache invalidated on dashboard update: dashboard=%s, keys_deleted=%d",
            dashboard_id, deleted_dash,
        )

    async def invalidate_kpis(self, connection_id: UUID) -> None:
        """Invalidate all KPI result caches for a connection."""
        pattern = CacheKeys.kpi_pattern(connection_id)
        deleted = await self._cache.delete_pattern(pattern)
        logger.debug("KPI cache invalidated: connection=%s, keys_deleted=%d", connection_id, deleted)
