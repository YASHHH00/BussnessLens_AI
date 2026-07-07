"""
BusinessLens AI — SchemaSnapshot ORM Model

Captures a point-in-time snapshot of a database schema.
Tracks table structures, column metadata, sample data, and data quality scores.
Enables schema drift detection by comparing consecutive snapshots.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, TenantMixin, generate_uuid


class SchemaSnapshot(Base, TenantMixin, TimestampMixin):
    """
    A complete schema scan result for one connection.

    Structure of `tables_json`:
    {
        "table_name": {
            "row_count": 12500,
            "columns": [
                {
                    "name": "order_date",
                    "physical_type": "timestamp",
                    "nullable": true,
                    "is_primary_key": false,
                    "sample_values": ["2024-01-15", "2024-02-03"],
                    "null_pct": 0.01,
                    "unique_pct": 0.95,
                    "min_value": "2023-01-01",
                    "max_value": "2024-12-31"
                },
                ...
            ]
        }
    }
    """

    __tablename__ = "schema_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    connection_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False, index=True
    )

    # Schema content
    tables_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    table_count: Mapped[int] = mapped_column(nullable=False, default=0)
    column_count: Mapped[int] = mapped_column(nullable=False, default=0)

    # Schema fingerprint — SHA-256 of sorted table/column names + types
    # Used to detect schema drift between scans
    schema_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # Scan metadata
    scan_duration_ms: Mapped[int | None] = mapped_column(nullable=True)
    scan_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_latest: Mapped[bool] = mapped_column(nullable=False, default=True, index=True)

    # Background job that produced this snapshot
    job_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)

    def __repr__(self) -> str:
        return (
            f"<SchemaSnapshot connection={self.connection_id} "
            f"tables={self.table_count} hash={self.schema_hash[:8]}>"
        )
