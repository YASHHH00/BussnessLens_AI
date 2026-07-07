"""
BusinessLens AI — Pydantic Schemas: Data Quality
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DataQualityIssue(BaseModel):
    column: str
    rule: str
    severity: str   # 'critical', 'warning', 'info'
    value: str
    message: str


class TableQualityScore(BaseModel):
    table: str
    score: float
    issues: list[DataQualityIssue]


class DataQualityReportResponse(BaseModel):
    id: UUID
    connection_id: UUID
    snapshot_id: UUID
    overall_score: float
    total_issues: int
    critical_issues: int
    warning_issues: int
    info_issues: int
    table_scores: list[TableQualityScore]
    created_at: datetime

    model_config = {"from_attributes": True}
