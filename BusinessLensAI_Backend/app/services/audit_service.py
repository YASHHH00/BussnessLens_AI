"""
BusinessLens AI — Audit Service
"""

from __future__ import annotations

from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.schemas.audit import AuditLogFilter, AuditLogListResponse, AuditLogResponse


class AuditService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_audit_logs(
        self,
        organization_id: UUID,
        filters: AuditLogFilter,
    ) -> AuditLogListResponse:
        stmt = select(AuditLog).where(AuditLog.organization_id == organization_id)

        if filters.action:
            stmt = stmt.where(AuditLog.action == filters.action)
        if filters.user_id:
            stmt = stmt.where(AuditLog.user_id == filters.user_id)
        if filters.resource_type:
            stmt = stmt.where(AuditLog.resource_type == filters.resource_type)
        if filters.date_from:
            stmt = stmt.where(AuditLog.created_at >= filters.date_from)
        if filters.date_to:
            stmt = stmt.where(AuditLog.created_at <= filters.date_to)

        # Total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self._db.execute(count_stmt)).scalar_one()

        # Pagination
        offset = (filters.page - 1) * filters.page_size
        stmt = stmt.order_by(AuditLog.created_at.desc()).offset(offset).limit(filters.page_size)

        result = await self._db.execute(stmt)
        items = list(result.scalars().all())

        return AuditLogListResponse(
            items=[AuditLogResponse.model_validate(i) for i in items],
            total=total,
        )
