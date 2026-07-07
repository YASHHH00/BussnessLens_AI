"""
BusinessLens AI — Mapping ORM Models

MappingSet: A named collection of field mappings for one connection.
FieldMapping: A single column-to-business-field mapping within a MappingSet.
SmartMappingMemory: Historical mapping patterns stored for reuse across connections.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Boolean, Float, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, TenantMixin, generate_uuid


class MappingSet(Base, TenantMixin, TimestampMixin):
    """
    A validated, named set of field mappings for a specific connection.

    One connection can have only one CONFIRMED MappingSet at a time.
    Previous confirmed sets are archived (is_active=False) when a new one is confirmed.
    Draft sets (status='draft') can coexist with the active confirmed set.

    Status lifecycle: 'draft' → 'ai_suggested' → 'confirmed'
    """

    __tablename__ = "mapping_sets"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    connection_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False, index=True
    )
    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="draft", index=True
    )  # 'draft' | 'ai_suggested' | 'confirmed'

    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, index=True
    )

    # AI analysis metadata
    ai_domain_fit_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_analyst_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_suggested_primary_table: Mapped[str | None] = mapped_column(String(256), nullable=True)
    join_hints: Mapped[list[dict]] = mapped_column(JSONB, nullable=False, default=list)

    # Confirmation metadata
    confirmed_by: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True
    )
    confirmed_at: Mapped[str | None] = mapped_column(String(64), nullable=True)

    created_by: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)

    def __repr__(self) -> str:
        return (
            f"<MappingSet name={self.name} status={self.status} "
            f"active={self.is_active}>"
        )


class FieldMapping(Base, TimestampMixin):
    """
    A single column-to-business-field mapping within a MappingSet.

    Each row represents one physical column from the source database
    mapped to one business field from the BusinessFieldRegistry.
    """

    __tablename__ = "field_mappings"
    __table_args__ = (
        # Unique: one column can only map to one field per MappingSet
        UniqueConstraint(
            "mapping_set_id", "table_name", "column_name",
            name="uq_field_mapping_col_per_set",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    mapping_set_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False, index=True
    )

    # Physical source
    table_name: Mapped[str] = mapped_column(String(256), nullable=False)
    column_name: Mapped[str] = mapped_column(String(256), nullable=False)
    physical_type: Mapped[str] = mapped_column(String(64), nullable=False, default="varchar")

    # Business field target
    business_field: Mapped[str | None] = mapped_column(String(128), nullable=True)
    # null = explicitly ignored/unmapped by the analyst

    # AI metadata
    ai_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_alternatives: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, default=list
    )

    # User override
    is_user_overridden: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    user_override_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Validation state
    is_validated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    validation_errors: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, default=list
    )

    def __repr__(self) -> str:
        return (
            f"<FieldMapping {self.table_name}.{self.column_name} "
            f"→ {self.business_field}>"
        )


class SmartMappingMemory(Base, TenantMixin, TimestampMixin):
    """
    Historical mapping pattern storage — enables Smart Mapping Memory.

    When a user confirms a mapping, successful column→field pairs are
    persisted here. On the next connection scan, these patterns are
    retrieved and fed into the AI cost optimizer as prior knowledge,
    reducing AI calls and improving accuracy.
    """

    __tablename__ = "smart_mapping_memory"
    __table_args__ = (
        UniqueConstraint(
            "organization_id", "column_name_normalized", "business_field",
            name="uq_memory_org_col_field",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )

    # Normalized column name (lowercased, stripped, underscores) for fuzzy matching
    column_name_normalized: Mapped[str] = mapped_column(
        String(256), nullable=False, index=True
    )
    # Original column names that contributed to this memory pattern
    original_examples: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, default=list
    )

    business_field: Mapped[str] = mapped_column(String(128), nullable=False)
    physical_type: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # How many times this pattern was confirmed
    confirm_count: Mapped[int] = mapped_column(nullable=False, default=1)
    avg_confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    def __repr__(self) -> str:
        return (
            f"<SmartMappingMemory {self.column_name_normalized} "
            f"→ {self.business_field} (×{self.confirm_count})>"
        )
