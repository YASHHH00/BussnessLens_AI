"""
BusinessLens AI — AI Analysis Service

Runs the AI schema analysis pipeline:
1. Load schema snapshot
2. Build prompt with field vocabulary
3. Call AI (via cost optimizer — cache-first)
4. Parse and return structured result

This service ONLY produces AISchemaAnalysisResult — it does NOT persist mappings.
MappingService reads this result and creates FieldMapping rows.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.base_provider import AIRequest, BaseAIProvider
from app.ai.cost_optimizer import AICostOptimizer
from app.ai.prompts.prompt_templates import (
    SCHEMA_ANALYSIS_SYSTEM,
    build_schema_analysis_prompt,
)
from app.cache.base_cache import BaseCacheProvider
from app.cache.cache_keys import CacheKeys
from app.core.exceptions import NotFoundError
from app.core.logging_config import get_logger
from app.registry.field_registry import BusinessFieldRegistry
from app.repositories.schema_repository import SchemaRepository
from app.schemas.ai_analysis import (
    AIColumnAnalysis,
    AISchemaAnalysisResult,
    AITableAnalysis,
)

logger = get_logger(__name__)


class AIAnalysisService:
    """
    Orchestrates AI schema analysis.

    Dependencies injected at call time:
    - AI provider (may be None → cost optimizer handles gracefully)
    - Cache provider (may be None → no caching)
    - Field registry (always available from app startup)
    """

    def __init__(
        self,
        db: AsyncSession,
        registry: BusinessFieldRegistry,
        ai_provider: BaseAIProvider | None = None,
        cache: BaseCacheProvider | None = None,
    ) -> None:
        self._schema_repo = SchemaRepository(db)
        self._registry = registry
        self._optimizer = AICostOptimizer(provider=ai_provider, cache=cache)

    async def analyze_schema(
        self,
        connection_id: UUID,
        organization_id: UUID,
        snapshot_id: UUID | None = None,
    ) -> AISchemaAnalysisResult:
        """
        Run AI schema analysis on the latest (or specified) snapshot.

        Returns a structured AISchemaAnalysisResult. The caller (MappingService)
        uses this result to create FieldMapping rows.
        """
        # Load snapshot
        if snapshot_id:
            from sqlalchemy import select
            from app.models.schema_snapshot import SchemaSnapshot
            stmt = select(SchemaSnapshot).where(SchemaSnapshot.id == snapshot_id)
            result = await self._schema_repo.db.execute(stmt)
            snapshot = result.scalar_one_or_none()
            if not snapshot:
                raise NotFoundError("SchemaSnapshot", snapshot_id)
        else:
            snapshot = await self._schema_repo.get_latest_for_connection(
                connection_id, organization_id
            )
            if not snapshot:
                raise NotFoundError("SchemaSnapshot", connection_id)

        # Cache key: keyed by (connection_id, schema_hash)
        cache_key = CacheKeys.ai_schema_analysis(connection_id, snapshot.schema_hash)

        # Build prompt
        field_vocabulary = self._registry.get_vocabulary_for_prompt()
        active_plugin = self._registry.get_active_plugin_metadata()
        domain_context = {
            "domain": active_plugin.get("domain", "retail"),
            "description": active_plugin.get("description", ""),
        }

        prompt = build_schema_analysis_prompt(
            tables_json=snapshot.tables_json,
            field_vocabulary=field_vocabulary,
            domain_context=domain_context,
        )

        request = AIRequest(
            prompt=prompt,
            system_instruction=SCHEMA_ANALYSIS_SYSTEM,
            temperature=0.1,    # Very low — we want deterministic schema analysis
            max_output_tokens=8192,
            response_format="json",
        )

        logger.info(
            "Running AI schema analysis: connection=%s snapshot=%s",
            connection_id, snapshot.id,
        )

        response = await self._optimizer.complete(
            request=request,
            cache_key=cache_key,
        )

        # Parse AI response
        raw = response.parse_json()
        return self._parse_analysis(raw, response)

    def _parse_analysis(self, raw: dict, response) -> AISchemaAnalysisResult:
        """Parse the AI JSON output into a typed AISchemaAnalysisResult."""
        table_analyses = []
        for table_name, table_data in raw.get("table_analyses", {}).items():
            columns = []
            for col in table_data.get("columns", []):
                alternatives = col.get("alternatives", col.get("ai_alternatives", []))
                columns.append(
                    AIColumnAnalysis(
                        column_name=col.get("column_name", ""),
                        business_field=col.get("business_field"),
                        confidence=float(col.get("confidence", 0.0)),
                        reasoning=col.get("reasoning", ""),
                        is_primary_key=bool(col.get("is_primary_key", False)),
                        data_quality_note=col.get("data_quality_note"),
                        ai_alternatives=alternatives if isinstance(alternatives, list) else [],
                    )
                )
            table_analyses.append(
                AITableAnalysis(
                    table_name=table_name,
                    purpose=table_data.get("purpose", ""),
                    columns=columns,
                )
            )

        return AISchemaAnalysisResult(
            table_analyses=table_analyses,
            suggested_primary_table=raw.get("suggested_primary_table"),
            join_hints=raw.get("join_hints", []),
            domain_fit_score=float(raw.get("domain_fit_score", 0.5)),
            analyst_notes=raw.get("analyst_notes", ""),
            provider=response.provider,
            model=response.model,
            total_tokens=response.total_tokens,
            cost_estimate_usd=response.cost_estimate_usd,
            latency_ms=response.latency_ms,
        )
