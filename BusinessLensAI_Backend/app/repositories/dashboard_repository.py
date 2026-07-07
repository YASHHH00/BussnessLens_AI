"""
BusinessLens AI — Dashboard Repository
"""

from __future__ import annotations

from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.dashboard import Dashboard, DashboardWidget
from app.repositories.base import BaseRepository


class DashboardRepository(BaseRepository[Dashboard]):
    model_class = Dashboard

    async def list_for_connection(self, connection_id: UUID, organization_id: UUID) -> list[Dashboard]:
        stmt = (
            select(Dashboard)
            .options(selectinload(Dashboard.widgets))
            .where(Dashboard.connection_id == connection_id, Dashboard.organization_id == organization_id)
            .order_by(Dashboard.is_default.desc(), Dashboard.created_at.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_with_widgets(self, dashboard_id: UUID, organization_id: UUID) -> Dashboard | None:
        stmt = (
            select(Dashboard)
            .options(selectinload(Dashboard.widgets))
            .where(Dashboard.id == dashboard_id, Dashboard.organization_id == organization_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
