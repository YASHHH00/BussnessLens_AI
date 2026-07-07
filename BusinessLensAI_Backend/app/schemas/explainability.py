"""
BusinessLens AI — Pydantic Schemas: Explainability

Used by GET /explain/{artifact_type}/{artifact_id}
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ExplanationResponse(BaseModel):
    """
    Serialized ExplanationContext for API consumers.
    `generated_sql` is role-gated — null for non Data Analyst / Admin roles.
    """
    artifact_type: str
    artifact_id: str
    title: str
    source_tables: list[str]
    source_columns: list[str]
    business_fields: list[str]
    aggregations: list[str]
    filters_applied: list[dict]
    formula: str | None
    related_kpis: list[str]
    generated_sql: str | None      # null if user lacks Data Analyst / Admin role
    rule_evaluation: str | None
    ai_reasoning_summary: str | None
    join_paths: list[str]
    date_range: str | None
    data_source: str
    computed_at: datetime
    confidence: float | None


class ExplainRequest(BaseModel):
    artifact_type: str
    artifact_id: UUID
