"""
BusinessLens AI — Semantic Service

Facade for the Semantic Layer — used by the API router.
Also exposes the context summary for the /semantic endpoint.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.base_cache import BaseCacheProvider
from app.core.exceptions import SemanticLayerError
from app.semantic.semantic_layer import SemanticLayer


class SemanticService:
    def __init__(
        self,
        db: AsyncSession,
        cache: BaseCacheProvider | None = None,
    ) -> None:
        self._layer = SemanticLayer(db=db, cache=cache)
        self._db = db

    async def get_context_summary(
        self, connection_id: UUID, organization_id: UUID
    ) -> dict:
        """Return a lightweight summary of the SemanticContext for a connection."""
        context = await self._layer.get_context(connection_id, organization_id)
        return context.to_summary_dict()

    async def get_full_context(
        self, connection_id: UUID, organization_id: UUID
    ) -> dict:
        """Return the full SemanticContext as a dict (for admin/debug use)."""
        context = await self._layer.get_context(connection_id, organization_id)
        return {
            **context.to_summary_dict(),
            "columns": [
                {
                    "table": c.table_name,
                    "column": c.column_name,
                    "type": c.physical_type,
                    "business_field": c.business_field,
                    "is_pk": c.is_primary_key,
                }
                for c in context.columns
            ],
            "join_paths": [
                {
                    "from": f"{jp.from_table}.{jp.from_column}",
                    "to": f"{jp.to_table}.{jp.to_column}",
                    "relationship": jp.relationship,
                }
                for jp in context.join_paths
            ],
        }

    async def invalidate(self, connection_id: UUID) -> None:
        """Manually invalidate the cached SemanticContext."""
        await self._layer.invalidate(connection_id)
