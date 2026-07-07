"""
BusinessLens AI — Schema Detection Service

Orchestrates schema scanning: connector → profiler → snapshot → drift detection.
Runs as a background job to avoid blocking the API response.
"""

from __future__ import annotations

import time
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.connectors.connector_factory import ConnectorFactory
from app.core.audit import AuditAction, emit_audit_log
from app.core.exceptions import NotFoundError
from app.core.logging_config import get_logger
from app.models.schema_snapshot import SchemaSnapshot
from app.repositories.connection_repository import ConnectionRepository
from app.repositories.schema_repository import SchemaRepository
from app.schemas.schema_detection import SchemaSnapshotResponse, SchemaDriftResponse
from app.utils.data_profiler import compute_schema_hash
from app.utils.schema_differ import compute_schema_diff

logger = get_logger(__name__)


class SchemaDetectionService:
    def __init__(self, db: AsyncSession) -> None:
        self._conn_repo = ConnectionRepository(db)
        self._schema_repo = SchemaRepository(db)
        self._db = db
        self._factory = ConnectorFactory()

    async def run_schema_scan(
        self,
        connection_id: UUID,
        organization_id: UUID,
        user_id: UUID,
    ) -> SchemaSnapshot:
        """
        Full schema scan pipeline:
        1. Load connection + connector
        2. Enumerate tables
        3. Inspect each table (columns + sample values)
        4. Compute schema hash
        5. Check for drift vs. previous snapshot
        6. Persist new snapshot (mark old as non-latest)
        7. Update connection's schema_version_hash
        8. Invalidate stale cache
        """
        connection = await self._conn_repo.get_by_id_or_raise(
            connection_id, organization_id, "Connection"
        )

        t0 = time.monotonic()
        connector = self._factory.create_from_model(connection)

        await emit_audit_log(
            db=self._db,
            action=AuditAction.SCHEMA_SCAN_STARTED,
            user_id=user_id,
            organization_id=organization_id,
            resource_type="connection",
            resource_id=connection_id,
        )

        try:
            async with connector:
                table_names = await connector.get_table_names()
                tables_json: dict = {}
                column_count = 0

                for table_name in table_names:
                    try:
                        meta = await connector.get_table_meta(table_name, sample_rows=5)
                        col_list = []
                        for col in meta.columns:
                            col_list.append({
                                "name": col.name,
                                "physical_type": col.physical_type,
                                "nullable": col.nullable,
                                "is_primary_key": col.is_primary_key,
                                "is_foreign_key": col.is_foreign_key,
                                "references": col.references,
                                "sample_values": meta.sample_values.get(col.name, []),
                            })
                            column_count += 1
                        tables_json[table_name] = {
                            "row_count": meta.row_count,
                            "columns": col_list,
                        }
                    except Exception as exc:
                        logger.warning("Failed to inspect table %s: %s", table_name, exc)
                        tables_json[table_name] = {"error": str(exc), "columns": []}

        except Exception as exc:
            logger.error("Schema scan failed for connection %s: %s", connection_id, exc)
            raise

        scan_duration_ms = int((time.monotonic() - t0) * 1000)
        schema_hash = compute_schema_hash(tables_json)

        # Mark existing snapshots as non-latest
        await self._schema_repo.mark_all_non_latest(connection_id)

        # Persist new snapshot
        snapshot = SchemaSnapshot(
            connection_id=connection_id,
            organization_id=organization_id,
            tables_json=tables_json,
            table_count=len(tables_json),
            column_count=column_count,
            schema_hash=schema_hash,
            scan_duration_ms=scan_duration_ms,
            is_latest=True,
        )
        snapshot = await self._schema_repo.create(snapshot)

        # Update connection hash
        await self._conn_repo.update_schema_hash(connection_id, schema_hash)

        await emit_audit_log(
            db=self._db,
            action=AuditAction.SCHEMA_SCAN_COMPLETED,
            user_id=user_id,
            organization_id=organization_id,
            resource_type="schema_snapshot",
            resource_id=snapshot.id,
            details={
                "tables": len(tables_json),
                "columns": column_count,
                "duration_ms": scan_duration_ms,
            },
        )

        logger.info(
            "Schema scan complete: connection=%s tables=%d columns=%d hash=%s",
            connection_id, len(tables_json), column_count, schema_hash[:8],
        )
        return snapshot

    async def get_latest_snapshot(
        self, connection_id: UUID, organization_id: UUID
    ) -> SchemaSnapshotResponse:
        snapshot = await self._schema_repo.get_latest_for_connection(
            connection_id, organization_id
        )
        if not snapshot:
            raise NotFoundError("SchemaSnapshot", connection_id)
        return SchemaSnapshotResponse(
            id=snapshot.id,
            connection_id=snapshot.connection_id,
            table_count=snapshot.table_count,
            column_count=snapshot.column_count,
            schema_hash=snapshot.schema_hash,
            is_latest=snapshot.is_latest,
            scan_duration_ms=snapshot.scan_duration_ms,
            tables=snapshot.tables_json,
            created_at=snapshot.created_at,
        )

    async def get_schema_diff(
        self, connection_id: UUID, organization_id: UUID
    ) -> SchemaDriftResponse:
        """Compare the two most recent snapshots to detect drift."""
        latest = await self._schema_repo.get_latest_for_connection(
            connection_id, organization_id
        )
        if not latest:
            raise NotFoundError("SchemaSnapshot", connection_id)

        previous = await self._schema_repo.get_previous_snapshot(
            connection_id, organization_id, exclude_id=latest.id
        )
        if not previous:
            return SchemaDriftResponse(
                has_changes=False,
                is_breaking=False,
                tables_added=[],
                tables_removed=[],
                column_changes=[],
            )

        diff = compute_schema_diff(previous.tables_json, latest.tables_json)
        return SchemaDriftResponse(**diff.to_dict())
