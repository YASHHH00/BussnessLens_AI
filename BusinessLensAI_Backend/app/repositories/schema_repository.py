"""
BusinessLens AI — Schema Repository
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select, update

from app.models.schema_snapshot import SchemaSnapshot
from app.repositories.base import BaseRepository


class SchemaRepository(BaseRepository[SchemaSnapshot]):
    model_class = SchemaSnapshot

    async def get_latest_for_connection(
        self, connection_id: UUID, organization_id: UUID
    ) -> SchemaSnapshot | None:
        stmt = (
            select(SchemaSnapshot)
            .where(
                SchemaSnapshot.connection_id == connection_id,
                SchemaSnapshot.organization_id == organization_id,
                SchemaSnapshot.is_latest == True,  # noqa: E712
            )
            .order_by(SchemaSnapshot.created_at.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_previous_snapshot(
        self, connection_id: UUID, organization_id: UUID, exclude_id: UUID
    ) -> SchemaSnapshot | None:
        stmt = (
            select(SchemaSnapshot)
            .where(
                SchemaSnapshot.connection_id == connection_id,
                SchemaSnapshot.organization_id == organization_id,
                SchemaSnapshot.id != exclude_id,
            )
            .order_by(SchemaSnapshot.created_at.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def mark_all_non_latest(self, connection_id: UUID) -> None:
        """Mark all snapshots for a connection as not-latest before inserting a new one."""
        await self.db.execute(
            update(SchemaSnapshot)
            .where(SchemaSnapshot.connection_id == connection_id)
            .values(is_latest=False)
        )

    async def list_for_connection(
        self, connection_id: UUID, organization_id: UUID, limit: int = 10
    ) -> list[SchemaSnapshot]:
        stmt = (
            select(SchemaSnapshot)
            .where(
                SchemaSnapshot.connection_id == connection_id,
                SchemaSnapshot.organization_id == organization_id,
            )
            .order_by(SchemaSnapshot.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
