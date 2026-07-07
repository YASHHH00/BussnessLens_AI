"""
BusinessLens AI — AI Insights Schemas
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class InsightItem(BaseModel):
    title: str
    body: str
    severity: str = Field("info", description="critical, warning, info, positive")
    metric: str
    recommended_action: str | None = None
    confidence: float = Field(0.9, ge=0.0, le=1.0)


class InsightGenerationResponse(BaseModel):
    executive_summary: str
    insights: list[InsightItem]
    generated_at: datetime
    provider: str
    model: str
    tokens_used: int
