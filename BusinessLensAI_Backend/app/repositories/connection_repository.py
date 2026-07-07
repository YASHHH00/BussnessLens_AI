"""
BusinessLens AI — Connection Repository
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select, update

from app.models.connection import DBConnection
from app.repositories.base import BaseRepository


class ConnectionRepository(BaseRepository[DBConnection]):
    model_class = DBConnection

    async def get_by_name(self, name: str, organization_id: UUID) -> DBConnection | None:
        stmt = select(DBConnection).where(
            DBConnection.name == name,
            DBConnection.organization_id == organization_id,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_schema_hash(self, connection_id: UUID, schema_hash: str) -> None:
        await self.db.execute(
            update(DBConnection)
            .where(DBConnection.id == connection_id)
            .values(schema_version_hash=schema_hash)
        )

    async def update_test_result(
        self, connection_id: UUID, succeeded: bool, tested_at: str
    ) -> None:
        await self.db.execute(
            update(DBConnection)
            .where(DBConnection.id == connection_id)
            .values(last_test_succeeded=succeeded, last_tested_at=tested_at)
        )
