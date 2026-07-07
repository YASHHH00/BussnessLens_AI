"""
BusinessLens AI — Analytics Pydantic Schemas

Defines the contract for analytics queries across time series, breakdowns,
and aggregated KPI metrics.
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class FilterCondition(BaseModel):
    """A single filter condition applied to a business field."""
    field: str
    operator: str = Field("eq", description="eq, neq, gt, gte, lt, lte, in, like")
    value: Any


class AnalyticsQueryRequest(BaseModel):
    """
    Metadata-driven query request.
    Consumers request metrics and dimensions by their standard business vocabulary names,
    NEVER by raw database table/column names.
    """
    metrics: list[str] = Field(..., min_length=1, description="List of business metric field names to compute")
    dimensions: list[str] = Field(default_factory=list, description="List of dimension/grouping field names")
    filters: list[FilterCondition] = Field(default_factory=list, description="Filters applied to query")
    date_range_field: str | None = Field(None, description="Temporal business field to filter date range")
    start_date: str | None = None
    end_date: str | None = None
    time_grain: str | None = Field(None, description="day, week, month, quarter, year")
    order_by: str | None = None
    order_direction: str = Field("desc", description="asc or desc")
    limit: int = Field(100, ge=1, le=10000)


class AnalyticsQueryResult(BaseModel):
    """Structured response from the Analytics Engine."""
    columns: list[str]
    rows: list[dict[str, Any]]
    total_rows: int
    execution_time_ms: int
    sql_executed: str | None = None  # Included only if user role allows debugging


class KPIEvaluationResult(BaseModel):
    """Result of a single KPI evaluation."""
    kpi_name: str
    display_name: str
    category: str
    current_value: float | None
    previous_value: float | None = None
    change_pct: float | None = None
    status: str = "normal"  # normal, warning, critical, positive
    formatted_value: str
    unit: str | None = None


class RuleTriggerAlert(BaseModel):
    """A triggered business rule / anomaly alert."""
    rule_name: str
    description: str
    severity: str  # info, warning, critical
    metric: str
    threshold_value: float | None
    actual_value: float | None
    message: str
