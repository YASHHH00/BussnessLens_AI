"""
BusinessLens AI — SQL Playground Schemas
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class SQLPlaygroundRequest(BaseModel):
    query: str = Field(..., min_length=5, max_length=10000, description="Read-only SQL statement")
    limit: int = Field(100, ge=1, le=1000)


class SQLPlaygroundResponse(BaseModel):
    query_executed: str
    columns: list[str]
    rows: list[dict[str, Any]]
    total_rows: int
    execution_time_ms: int
