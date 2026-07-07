"""
BusinessLens AI — Mapping Service

Full mapping workflow:
  1. Trigger AI analysis → AISchemaAnalysisResult
  2. Create MappingSet (status='ai_suggested') + FieldMapping rows
  3. Apply user overrides
  4. Validate with MappingValidationEngine (10 rules)
  5. Confirm → update SmartMappingMemory → invalidate SemanticContext cache
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.base_cache import BaseCacheProvider
from app.core.audit import AuditAction, emit_audit_log
from app.core.exceptions import MappingValidationError, NotFoundError
from app.core.logging_config import get_logger
from app.engines.mapping_validation_engine import MappingValidationEngine
from app.models.mapping import FieldMapping, MappingSet
from app.registry.field_registry import BusinessFieldRegistry
from app.repositories.mapping_repository import (
    FieldMappingRepository,
    MappingSetRepository,
    SmartMappingMemoryRepository,
)
from app.repositories.schema_repository import SchemaRepository
from app.schemas.mapping import (
    FieldMappingItem,
    FieldMappingResponse,
    MappingSetResponse,
)
from app.semantic.semantic_layer import SemanticLayer

logger = get_logger(__name__)

_NORMALIZE_TABLE = str.maketrans(" -", "__")


def _normalize_column_name(name: str) -> str:
    """Normalize: lowercase, replace spaces/hyphens with underscores, strip."""
    return name.strip().lower().translate(_NORMALIZE_TABLE)


class MappingService:
    def __init__(
        self,
        db: AsyncSession,
        registry: BusinessFieldRegistry,
        ai_provider=None,
        cache: BaseCacheProvider | None = None,
    ) -> None:
        self._db = db
        self._registry = registry
        self._ai_provider = ai_provider
        self._cache = cache
        self._ms_repo = MappingSetRepository(db)
        self._fm_repo = FieldMappingRepository(db)
        self._mem_repo = SmartMappingMemoryRepository(db)
        self._schema_repo = SchemaRepository(db)
        self._validation_engine = MappingValidationEngine(registry)

    # ------------------------------------------------------------------ #
    # 1. Trigger AI analysis + create draft MappingSet
    # ------------------------------------------------------------------ #

    async def create_from_ai_analysis(
        self,
        connection_id: UUID,
        organization_id: UUID,
        user_id: UUID,
        snapshot_id: UUID | None = None,
        name: str | None = None,
    ) -> MappingSetResponse:
        """
        Run AI analysis on the latest schema snapshot and create a draft MappingSet.
        Applies Smart Mapping Memory to boost AI suggestion confidence.
        """
        from app.services.ai_analysis_service import AIAnalysisService

        # Fetch Smart Mapping Memory for this org
        memory_patterns = await self._mem_repo.get_all_for_org(organization_id)
        memory_map = {m.column_name_normalized: m for m in memory_patterns}

        # Run AI analysis
        ai_svc = AIAnalysisService(
            db=self._db,
            registry=self._registry,
            ai_provider=self._ai_provider,
            cache=self._cache,
        )
        analysis = await ai_svc.analyze_schema(
            connection_id=connection_id,
            organization_id=organization_id,
            snapshot_id=snapshot_id,
        )

        # Get snapshot for reference
        snapshot = await self._schema_repo.get_latest_for_connection(
            connection_id, organization_id
        )

        # Create MappingSet
        ms_name = name or f"Auto-mapping {datetime.now(UTC).strftime('%Y-%m-%d %H:%M')}"
        mapping_set = MappingSet(
            connection_id=connection_id,
            organization_id=organization_id,
            snapshot_id=snapshot.id if snapshot else UUID(int=0),
            name=ms_name,
            status="ai_suggested",
            is_active=False,
            ai_domain_fit_score=analysis.domain_fit_score,
            ai_analyst_notes=analysis.analyst_notes,
            ai_suggested_primary_table=analysis.suggested_primary_table,
            join_hints=analysis.join_hints,
            created_by=user_id,
        )
        mapping_set = await self._ms_repo.create(mapping_set)

        # Create FieldMapping rows
        field_mappings: list[FieldMapping] = []
        snapshot_tables = snapshot.tables_json if snapshot else {}

        for table_analysis in analysis.table_analyses:
            snap_table = snapshot_tables.get(table_analysis.table_name, {})

            for col_analysis in table_analysis.columns:
                # Check Smart Memory for override
                norm_name = _normalize_column_name(col_analysis.column_name)
                memory_entry = memory_map.get(norm_name)

                # Prefer memory over AI if memory confidence is higher
                if (
                    memory_entry
                    and memory_entry.avg_confidence > col_analysis.confidence
                    and memory_entry.business_field != col_analysis.business_field
                ):
                    business_field = memory_entry.business_field
                    confidence = memory_entry.avg_confidence
                    reasoning = (
                        f"Smart Mapping Memory: previously confirmed {memory_entry.confirm_count}× "
                        f"as '{business_field}' (avg confidence {memory_entry.avg_confidence:.2f}). "
                        f"AI suggested: {col_analysis.business_field or 'unmapped'}."
                    )
                else:
                    business_field = col_analysis.business_field
                    confidence = col_analysis.confidence
                    reasoning = col_analysis.reasoning

                # Get physical type from snapshot
                physical_type = "varchar"
                for snap_col in snap_table.get("columns", []):
                    if snap_col.get("name") == col_analysis.column_name:
                        physical_type = snap_col.get("physical_type", "varchar")
                        break

                fm = FieldMapping(
                    mapping_set_id=mapping_set.id,
                    table_name=table_analysis.table_name,
                    column_name=col_analysis.column_name,
                    physical_type=physical_type,
                    business_field=business_field,
                    ai_confidence=confidence,
                    ai_reasoning=reasoning,
                    ai_alternatives=col_analysis.ai_alternatives,
                    is_user_overridden=False,
                    is_validated=False,
                )
                field_mappings.append(fm)

        await self._fm_repo.create_many(field_mappings)

        await emit_audit_log(
            db=self._db,
            action=AuditAction.MAPPING_CREATED,
            user_id=user_id,
            organization_id=organization_id,
            resource_type="mapping_set",
            resource_id=mapping_set.id,
            details={
                "name": mapping_set.name,
                "domain_fit_score": analysis.domain_fit_score,
                "field_mappings": len(field_mappings),
            },
        )

        return await self._to_response(mapping_set)

    # ------------------------------------------------------------------ #
    # 2. Validate a MappingSet
    # ------------------------------------------------------------------ #

    async def validate_mapping_set(
        self, mapping_set_id: UUID, organization_id: UUID
    ) -> dict:
        """
        Run all 10 validation rules against a MappingSet.
        Returns validation summary — does NOT persist.
        """
        mapping_set = await self._ms_repo.get_by_id_or_raise(
            mapping_set_id, organization_id, "MappingSet"
        )
        field_mappings = await self._fm_repo.get_for_mapping_set(mapping_set_id)
        snapshot = await self._schema_repo.get_latest_for_connection(
            mapping_set.connection_id, organization_id
        )
        snapshot_tables = snapshot.tables_json if snapshot else {}

        # Prepare flat mapping list for validation
        validation_input = [
            {
                "table": fm.table_name,
                "column": fm.column_name,
                "business_field": fm.business_field,
                "physical_type": fm.physical_type,
                "is_pk": False,
            }
            for fm in field_mappings
        ]

        violations = self._validation_engine.validate(validation_input, snapshot_tables)
        errors = [v for v in violations if v.severity == "error"]
        warnings = [v for v in violations if v.severity == "warning"]

        return {
            "mapping_set_id": str(mapping_set_id),
            "is_valid": len(errors) == 0,
            "error_count": len(errors),
            "warning_count": len(warnings),
            "violations": [
                {
                    "rule": v.rule,
                    "message": v.message,
                    "severity": v.severity,
                    "column": v.column,
                    "field": v.field,
                }
                for v in violations
            ],
        }

    # ------------------------------------------------------------------ #
    # 3. Confirm a MappingSet
    # ------------------------------------------------------------------ #

    async def confirm_mapping_set(
        self,
        mapping_set_id: UUID,
        organization_id: UUID,
        user_id: UUID,
        overrides: list[FieldMappingItem] | None = None,
    ) -> MappingSetResponse:
        """
        Confirm a mapping set with optional user overrides.

        Steps:
        1. Apply user overrides
        2. Validate (must pass all ERROR rules)
        3. Archive previous confirmed set
        4. Mark this set as confirmed + active
        5. Update Smart Mapping Memory
        6. Invalidate SemanticContext cache
        """
        mapping_set = await self._ms_repo.get_by_id_or_raise(
            mapping_set_id, organization_id, "MappingSet"
        )
        field_mappings = await self._fm_repo.get_for_mapping_set(mapping_set_id)
        snapshot = await self._schema_repo.get_latest_for_connection(
            mapping_set.connection_id, organization_id
        )
        snapshot_tables = snapshot.tables_json if snapshot else {}

        # Apply overrides
        if overrides:
            override_map = {
                (o.table_name, o.column_name): o for o in overrides
            }
            for fm in field_mappings:
                key = (fm.table_name, fm.column_name)
                if key in override_map:
                    override = override_map[key]
                    await self._fm_repo.update_mapping(
                        field_mapping_id=fm.id,
                        business_field=override.business_field,
                        is_user_overridden=True,
                        user_override_note=override.user_override_note,
                    )
                    fm.business_field = override.business_field
                    fm.is_user_overridden = True

        # Validate
        validation_input = [
            {
                "table": fm.table_name,
                "column": fm.column_name,
                "business_field": fm.business_field,
                "physical_type": fm.physical_type,
                "is_pk": False,
            }
            for fm in field_mappings
        ]
        violations = self._validation_engine.validate(validation_input, snapshot_tables)
        if self._validation_engine.has_blocking_errors(violations):
            raise MappingValidationError(
                violations=[v.message for v in violations if v.severity == "error"]
            )

        # Archive previous confirmed set
        await self._ms_repo.deactivate_all_for_connection(mapping_set.connection_id)

        # Confirm
        confirmed_at = datetime.now(UTC).isoformat()
        await self._ms_repo.set_confirmed(mapping_set_id, user_id, confirmed_at)

        # Update Smart Mapping Memory
        for fm in field_mappings:
            if fm.business_field:
                await self._mem_repo.upsert_memory(
                    organization_id=organization_id,
                    column_name_normalized=_normalize_column_name(fm.column_name),
                    column_name_original=fm.column_name,
                    business_field=fm.business_field,
                    physical_type=fm.physical_type,
                    confidence=fm.ai_confidence or 1.0,
                )

        # Invalidate SemanticContext cache
        semantic_layer = SemanticLayer(db=self._db, cache=self._cache)
        await semantic_layer.invalidate(mapping_set.connection_id)

        await emit_audit_log(
            db=self._db,
            action=AuditAction.MAPPING_CONFIRMED,
            user_id=user_id,
            organization_id=organization_id,
            resource_type="mapping_set",
            resource_id=mapping_set_id,
            details={"name": mapping_set.name},
        )

        logger.info(
            "Mapping confirmed: mapping_set=%s connection=%s",
            mapping_set_id, mapping_set.connection_id,
        )

        # Reload
        from sqlalchemy import select
        from app.models.mapping import MappingSet as MS
        stmt = select(MS).where(MS.id == mapping_set_id)
        result = await self._db.execute(stmt)
        updated_ms = result.scalar_one()
        return await self._to_response(updated_ms)

    # ------------------------------------------------------------------ #
    # Read operations
    # ------------------------------------------------------------------ #

    async def get_mapping_set(
        self, mapping_set_id: UUID, organization_id: UUID
    ) -> MappingSetResponse:
        ms = await self._ms_repo.get_by_id_or_raise(
            mapping_set_id, organization_id, "MappingSet"
        )
        return await self._to_response(ms)

    async def list_mapping_sets(
        self, connection_id: UUID, organization_id: UUID
    ) -> list[MappingSetResponse]:
        sets = await self._ms_repo.list_for_connection(connection_id, organization_id)
        return [await self._to_response(ms) for ms in sets]

    # ------------------------------------------------------------------ #
    # Private
    # ------------------------------------------------------------------ #

    async def _to_response(self, ms: MappingSet) -> MappingSetResponse:
        field_mappings = await self._fm_repo.get_for_mapping_set(ms.id)
        fm_responses = [
            FieldMappingResponse(
                id=fm.id,
                mapping_set_id=fm.mapping_set_id,
                table_name=fm.table_name,
                column_name=fm.column_name,
                physical_type=fm.physical_type,
                business_field=fm.business_field,
                ai_confidence=fm.ai_confidence,
                ai_reasoning=fm.ai_reasoning,
                ai_alternatives=fm.ai_alternatives or [],
                is_user_overridden=fm.is_user_overridden,
                is_validated=fm.is_validated,
                validation_errors=fm.validation_errors or [],
            )
            for fm in field_mappings
        ]
        return MappingSetResponse(
            id=ms.id,
            connection_id=ms.connection_id,
            snapshot_id=ms.snapshot_id,
            name=ms.name,
            description=ms.description,
            status=ms.status,
            is_active=ms.is_active,
            ai_domain_fit_score=ms.ai_domain_fit_score,
            ai_analyst_notes=ms.ai_analyst_notes,
            ai_suggested_primary_table=ms.ai_suggested_primary_table,
            join_hints=ms.join_hints or [],
            confirmed_by=ms.confirmed_by,
            confirmed_at=ms.confirmed_at,
            created_at=ms.created_at,
            field_mappings=fm_responses,
        )
