"""
BusinessLens AI — Pydantic Schemas: AI Analysis
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class AIAnalysisRequest(BaseModel):
    connection_id: str
    snapshot_id: str


class AIColumnAnalysis(BaseModel):
    column_name: str
    business_field: str | None
    confidence: float
    reasoning: str
    is_primary_key: bool = False
    data_quality_note: str | None = None
    ai_alternatives: list[str] = Field(default_factory=list)


class AITableAnalysis(BaseModel):
    table_name: str
    purpose: str
    columns: list[AIColumnAnalysis]


class AISchemaAnalysisResult(BaseModel):
    """Full AI analysis result for a schema snapshot."""
    table_analyses: list[AITableAnalysis]
    suggested_primary_table: str | None
    join_hints: list[dict]
    domain_fit_score: float
    analyst_notes: str
    provider: str
    model: str
    total_tokens: int
    cost_estimate_usd: float | None
    latency_ms: int
