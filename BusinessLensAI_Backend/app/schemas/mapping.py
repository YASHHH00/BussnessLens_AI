"""
BusinessLens AI — Mapping Pydantic Schemas
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class FieldMappingItem(BaseModel):
    """A single column-to-field mapping in a create/update request."""
    table_name: str
    column_name: str
    physical_type: str = "varchar"
    business_field: str | None = None
    is_user_overridden: bool = False
    user_override_note: str | None = None


class MappingSetCreateRequest(BaseModel):
    connection_id: UUID
    snapshot_id: UUID
    name: str = Field(min_length=1, max_length=256)
    description: str | None = None


class MappingConfirmRequest(BaseModel):
    """Confirm a mapping set — triggers SmartMappingMemory update and Semantic Layer reload."""
    mapping_set_id: UUID
    overrides: list[FieldMappingItem] = Field(
        default_factory=list,
        description="User-defined overrides applied before confirmation.",
    )


class FieldMappingResponse(BaseModel):
    id: UUID
    mapping_set_id: UUID
    table_name: str
    column_name: str
    physical_type: str
    business_field: str | None
    ai_confidence: float | None
    ai_reasoning: str | None
    ai_alternatives: list[str]
    is_user_overridden: bool
    is_validated: bool
    validation_errors: list[str]

    model_config = {"from_attributes": True}


class MappingSetResponse(BaseModel):
    id: UUID
    connection_id: UUID
    snapshot_id: UUID
    name: str
    description: str | None
    status: str
    is_active: bool
    ai_domain_fit_score: float | None
    ai_analyst_notes: str | None
    ai_suggested_primary_table: str | None
    join_hints: list[dict]
    confirmed_by: UUID | None
    confirmed_at: str | None
    created_at: datetime
    field_mappings: list[FieldMappingResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class MappingListResponse(BaseModel):
    mapping_sets: list[MappingSetResponse]
    total: int


class SmartMemoryEntry(BaseModel):
    column_name_normalized: str
    business_field: str
    confirm_count: int
    avg_confidence: float

    model_config = {"from_attributes": True}
