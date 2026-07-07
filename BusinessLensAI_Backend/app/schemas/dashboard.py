"""
BusinessLens AI — Dashboard Pydantic Schemas
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, Field


class WidgetCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=256)
    widget_type: str = Field(..., description="kpi_card, line_chart, bar_chart, pie_chart, table")
    query_config: dict[str, Any] = Field(..., description="AnalyticsQueryRequest payload dict")
    position: int = Field(0, ge=0)
    width_span: int = Field(6, ge=1, le=12)


class DashboardCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=256)
    description: str | None = None
    is_default: bool = False
    widgets: list[WidgetCreateRequest] = Field(default_factory=list)


class WidgetResponse(BaseModel):
    id: UUID
    dashboard_id: UUID
    title: str
    widget_type: str
    query_config: dict[str, Any]
    position: int
    width_span: int

    model_config = {"from_attributes": True}


class DashboardResponse(BaseModel):
    id: UUID
    connection_id: UUID
    name: str
    description: str | None
    is_default: bool
    layout_json: dict[str, Any]
    created_at: datetime
    updated_at: datetime
    widgets: list[WidgetResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class DashboardListResponse(BaseModel):
    dashboards: list[DashboardResponse]
    total: int
