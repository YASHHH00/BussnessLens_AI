"""
BusinessLens AI — Audit Log API Router
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, require_role
from app.core.database import get_db
from app.schemas.audit import AuditLogFilter, AuditLogListResponse
from app.services.audit_service import AuditService

router = APIRouter(prefix="/audit", tags=["Audit Log"], dependencies=[require_role("admin")])


@router.get("", response_model=AuditLogListResponse)
async def list_audit_logs(
    filter_params: AuditLogFilter = Depends(),
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Query immutable platform audit logs filtered by action, user, or date range.
    Restricted to Organization Admins.
    """
    svc = AuditService(db)
    return await svc.list_audit_logs(current_user.organization_id, filter_params)
