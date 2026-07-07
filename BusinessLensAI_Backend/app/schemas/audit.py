"""
BusinessLens AI — Pydantic Schemas: Audit Log
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.common import PaginationParams


class AuditLogResponse(BaseModel):
    id: UUID
    action: str
    user_id: UUID
    organization_id: UUID
    resource_type: str
    resource_id: UUID | None
    details: dict
    ip_address: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditLogFilter(BaseModel):
    """Query parameters for filtering audit logs."""
    action: str | None = None
    user_id: UUID | None = None
    resource_type: str | None = None
    resource_id: UUID | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    page: int = 1
    page_size: int = 50


class AuditLogListResponse(BaseModel):
    items: list[AuditLogResponse]
    total: int

