"""
BusinessLens AI — Pydantic Schemas: Schema Detection
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ColumnMetaResponse(BaseModel):
    name: str
    physical_type: str
    nullable: bool
    is_primary_key: bool
    is_foreign_key: bool
    references: str | None
    sample_values: list


class TableMetaResponse(BaseModel):
    name: str
    row_count: int | None
    columns: list[ColumnMetaResponse]


class SchemaSnapshotResponse(BaseModel):
    id: UUID
    connection_id: UUID
    table_count: int
    column_count: int
    schema_hash: str
    is_latest: bool
    scan_duration_ms: int | None
    tables: dict
    created_at: datetime

    model_config = {"from_attributes": True}


class SchemaDriftResponse(BaseModel):
    has_changes: bool
    is_breaking: bool
    tables_added: list[str]
    tables_removed: list[str]
    column_changes: list[dict]


class SchemaJobResponse(BaseModel):
    job_id: UUID
    status: str
    message: str
