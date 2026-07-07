"""
BusinessLens AI — Semantic Layer

Builds and caches SemanticContext from confirmed MappingSets.
This is the central component that decouples mapping storage
from all downstream analytics/AI/forecasting engines.

Architecture:
  MappingSet (DB) → SemanticLayer.build() → SemanticContext (in-memory / cache)
                                              ↓
                    Analytics Engine, KPI Engine, Dashboard, AI, Forecasting
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.base_cache import BaseCacheProvider
from app.cache.cache_keys import CacheKeys
from app.core.exceptions import NotFoundError, SemanticLayerError
from app.core.logging_config import get_logger
from app.models.mapping import FieldMapping, MappingSet
from app.models.schema_snapshot import SchemaSnapshot
from app.semantic.semantic_context import SemanticColumn, SemanticContext, SemanticJoinPath

logger = get_logger(__name__)


class SemanticLayer:
    """
    Builds SemanticContext from persisted MappingSet data.

    Cache policy:
    - SemanticContext is cached keyed by (connection_id, mapping_set_id).
    - Invalidated on: mapping confirmation, schema rescan, manual invalidation.
    - TTL: CACHE_SCHEMA_ANALYSIS_TTL_SECONDS (default 3600s).
    """

    def __init__(
        self,
        db: AsyncSession,
        cache: BaseCacheProvider | None = None,
    ) -> None:
        self._db = db
        self._cache = cache

    async def get_context(
        self, connection_id: UUID, organization_id: UUID
    ) -> SemanticContext:
        """
        Get the SemanticContext for a connection.
        Returns the cached context if available; builds from DB otherwise.

        Raises SemanticLayerError if no confirmed mapping exists for the connection.
        """
        cache_key = CacheKeys.semantic_context(connection_id)

        # Cache check
        if self._cache:
            cached = await self._cache.get(cache_key)
            if cached:
                logger.debug("Semantic cache hit: connection=%s", connection_id)
                return self._deserialize(cached)

        # Build from DB
        context = await self._build_from_db(connection_id, organization_id)

        # Store in cache
        if self._cache:
            from app.core.config import settings
            await self._cache.set(
                cache_key,
                self._serialize(context),
                ttl_seconds=settings.CACHE_SCHEMA_ANALYSIS_TTL_SECONDS,
            )

        return context

    async def invalidate(self, connection_id: UUID) -> None:
        """Invalidate the cached SemanticContext for a connection."""
        if self._cache:
            cache_key = CacheKeys.semantic_context(connection_id)
            await self._cache.delete(cache_key)
            logger.info("Semantic context invalidated for connection=%s", connection_id)

    async def _build_from_db(
        self, connection_id: UUID, organization_id: UUID
    ) -> SemanticContext:
        """
        Build SemanticContext from the confirmed MappingSet.
        """
        # Load the confirmed active mapping set
        ms_stmt = (
            select(MappingSet)
            .where(
                MappingSet.connection_id == connection_id,
                MappingSet.organization_id == organization_id,
                MappingSet.status == "confirmed",
                MappingSet.is_active == True,  # noqa: E712
            )
            .order_by(MappingSet.created_at.desc())
            .limit(1)
        )
        result = await self._db.execute(ms_stmt)
        mapping_set: MappingSet | None = result.scalar_one_or_none()

        if mapping_set is None:
            raise SemanticLayerError(
                f"No confirmed mapping set found for connection {connection_id}. "
                "Please complete the mapping workflow first."
            )

        # Load field mappings
        fm_stmt = select(FieldMapping).where(
            FieldMapping.mapping_set_id == mapping_set.id
        )
        fm_result = await self._db.execute(fm_stmt)
        field_mappings = fm_result.scalars().all()

        # Load the associated schema snapshot for column metadata
        ss_stmt = select(SchemaSnapshot).where(
            SchemaSnapshot.id == mapping_set.snapshot_id
        )
        ss_result = await self._db.execute(ss_stmt)
        snapshot: SchemaSnapshot | None = ss_result.scalar_one_or_none()
        snapshot_tables = snapshot.tables_json if snapshot else {}

        # Build SemanticColumns
        semantic_columns = self._build_semantic_columns(
            field_mappings, snapshot_tables
        )

        # Build SemanticJoinPaths from join hints + FK metadata
        join_paths = self._build_join_paths(
            mapping_set.join_hints, snapshot_tables
        )

        context = SemanticContext(
            connection_id=connection_id,
            mapping_set_id=mapping_set.id,
            organization_id=organization_id,
            columns=semantic_columns,
            join_paths=join_paths,
            primary_table=mapping_set.ai_suggested_primary_table,
        )

        logger.info(
            "Semantic context built: connection=%s tables=%d fields=%d joins=%d",
            connection_id, len(context.list_tables()),
            len(context.list_mapped_fields()), len(join_paths),
        )
        return context

    def _build_semantic_columns(
        self, field_mappings: list[FieldMapping], snapshot_tables: dict
    ) -> list[SemanticColumn]:
        """Convert FieldMapping rows to SemanticColumn objects."""
        columns = []
        for fm in field_mappings:
            # Get column metadata from snapshot
            snap_col_meta = {}
            if fm.table_name in snapshot_tables:
                for col in snapshot_tables[fm.table_name].get("columns", []):
                    if col.get("name") == fm.column_name:
                        snap_col_meta = col
                        break

            columns.append(
                SemanticColumn(
                    table_name=fm.table_name,
                    column_name=fm.column_name,
                    physical_type=fm.physical_type,
                    business_field=fm.business_field,
                    is_primary_key=snap_col_meta.get("is_primary_key", False),
                    is_foreign_key=snap_col_meta.get("is_foreign_key", False),
                    references=snap_col_meta.get("references"),
                )
            )
        return columns

    def _build_join_paths(
        self, join_hints: list[dict], snapshot_tables: dict
    ) -> list[SemanticJoinPath]:
        """Build join paths from AI join hints."""
        paths = []
        for hint in join_hints:
            try:
                paths.append(
                    SemanticJoinPath(
                        from_table=hint["from_table"],
                        from_column=hint["from_column"],
                        to_table=hint["to_table"],
                        to_column=hint["to_column"],
                        relationship=hint.get("relationship", "many-to-one"),
                    )
                )
            except KeyError:
                logger.warning("Malformed join hint: %s", hint)
        return paths

    # ------------------------------------------------------------------ #
    # Serialization helpers (for cache storage)
    # ------------------------------------------------------------------ #

    def _serialize(self, context: SemanticContext) -> dict:
        return {
            "connection_id": str(context.connection_id),
            "mapping_set_id": str(context.mapping_set_id),
            "organization_id": str(context.organization_id),
            "primary_table": context.primary_table,
            "columns": [
                {
                    "table_name": c.table_name,
                    "column_name": c.column_name,
                    "physical_type": c.physical_type,
                    "business_field": c.business_field,
                    "is_primary_key": c.is_primary_key,
                    "is_foreign_key": c.is_foreign_key,
                    "references": c.references,
                }
                for c in context.columns
            ],
            "join_paths": [
                {
                    "from_table": jp.from_table,
                    "from_column": jp.from_column,
                    "to_table": jp.to_table,
                    "to_column": jp.to_column,
                    "relationship": jp.relationship,
                }
                for jp in context.join_paths
            ],
        }

    def _deserialize(self, data: dict) -> SemanticContext:
        columns = [SemanticColumn(**c) for c in data["columns"]]
        join_paths = [SemanticJoinPath(**jp) for jp in data["join_paths"]]
        return SemanticContext(
            connection_id=UUID(data["connection_id"]),
            mapping_set_id=UUID(data["mapping_set_id"]),
            organization_id=UUID(data["organization_id"]),
            primary_table=data.get("primary_table"),
            columns=columns,
            join_paths=join_paths,
        )
