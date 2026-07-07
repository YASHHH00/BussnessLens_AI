"""
BusinessLens AI — Admin & AI Cost Monitoring Schemas
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel


class AICostStatsResponse(BaseModel):
    provider: str
    total_calls: int
    total_tokens: int
    cache_hits: int
    estimated_cost_usd: float


class SystemHealthResponse(BaseModel):
    status: str  # healthy, degraded
    db_connection: bool
    active_connections_count: int
    cached_queries_count: int
    details: dict[str, Any]
