"""
BusinessLens AI — Report Export Schemas
"""

from __future__ import annotations

from uuid import UUID
from pydantic import BaseModel, Field


class ReportExportRequest(BaseModel):
    title: str = Field("Executive BI Report", min_length=1, max_length=256)
    dashboard_id: UUID | None = None
    format: str = Field("xlsx", description="xlsx or json")
    include_raw_data: bool = True
