"""
BusinessLens AI — Mapping Repository

Handles all persistence for MappingSet, FieldMapping, and SmartMappingMemory.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select, update

from app.models.mapping import FieldMapping, MappingSet, SmartMappingMemory
from app.repositories.base import BaseRepository


class MappingSetRepository(BaseRepository[MappingSet]):
    model_class = MappingSet

    async def get_active_for_connection(
        self, connection_id: UUID, organization_id: UUID
    ) -> MappingSet | None:
        stmt = (
            select(MappingSet)
            .where(
                MappingSet.connection_id == connection_id,
                MappingSet.organization_id == organization_id,
                MappingSet.status == "confirmed",
                MappingSet.is_active == True,  # noqa: E712
            )
            .order_by(MappingSet.created_at.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_for_connection(
        self, connection_id: UUID, organization_id: UUID
    ) -> list[MappingSet]:
        stmt = (
            select(MappingSet)
            .where(
                MappingSet.connection_id == connection_id,
                MappingSet.organization_id == organization_id,
            )
            .order_by(MappingSet.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def deactivate_all_for_connection(self, connection_id: UUID) -> None:
        """Archive all previously confirmed sets when a new one is confirmed."""
        await self.db.execute(
            update(MappingSet)
            .where(MappingSet.connection_id == connection_id)
            .values(is_active=False)
        )

    async def set_confirmed(
        self,
        mapping_set_id: UUID,
        confirmed_by: UUID,
        confirmed_at: str,
    ) -> None:
        await self.db.execute(
            update(MappingSet)
            .where(MappingSet.id == mapping_set_id)
            .values(
                status="confirmed",
                is_active=True,
                confirmed_by=confirmed_by,
                confirmed_at=confirmed_at,
            )
        )


class FieldMappingRepository:
    """Field-level mapping operations — not tenant-scoped (scoped via MappingSet)."""

    def __init__(self, db) -> None:
        self.db = db

    async def get_for_mapping_set(self, mapping_set_id: UUID) -> list[FieldMapping]:
        stmt = select(FieldMapping).where(
            FieldMapping.mapping_set_id == mapping_set_id
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_many(self, mappings: list[FieldMapping]) -> list[FieldMapping]:
        for m in mappings:
            self.db.add(m)
        await self.db.flush(mappings)
        return mappings

    async def update_mapping(
        self,
        field_mapping_id: UUID,
        business_field: str | None,
        is_user_overridden: bool,
        user_override_note: str | None,
    ) -> None:
        await self.db.execute(
            update(FieldMapping)
            .where(FieldMapping.id == field_mapping_id)
            .values(
                business_field=business_field,
                is_user_overridden=is_user_overridden,
                user_override_note=user_override_note,
            )
        )


class SmartMappingMemoryRepository:
    """Memory pattern storage for Smart Mapping Memory feature."""

    def __init__(self, db) -> None:
        self.db = db

    async def get_all_for_org(
        self, organization_id: UUID, limit: int = 200
    ) -> list[SmartMappingMemory]:
        stmt = (
            select(SmartMappingMemory)
            .where(SmartMappingMemory.organization_id == organization_id)
            .order_by(SmartMappingMemory.confirm_count.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def find_by_normalized_column(
        self, organization_id: UUID, column_name_normalized: str
    ) -> SmartMappingMemory | None:
        stmt = select(SmartMappingMemory).where(
            SmartMappingMemory.organization_id == organization_id,
            SmartMappingMemory.column_name_normalized == column_name_normalized,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert_memory(
        self,
        organization_id: UUID,
        column_name_normalized: str,
        column_name_original: str,
        business_field: str,
        physical_type: str | None,
        confidence: float,
    ) -> None:
        """Upsert a memory pattern — increment count if exists, insert if new."""
        existing = await self.find_by_normalized_column(
            organization_id, column_name_normalized
        )

        if existing:
            # Update existing
            new_count = existing.confirm_count + 1
            new_avg = (
                existing.avg_confidence * existing.confirm_count + confidence
            ) / new_count
            new_examples = list(set(existing.original_examples + [column_name_original]))[:10]
            await self.db.execute(
                update(SmartMappingMemory)
                .where(SmartMappingMemory.id == existing.id)
                .values(
                    confirm_count=new_count,
                    avg_confidence=new_avg,
                    original_examples=new_examples,
                )
            )
        else:
            # Insert new
            memory = SmartMappingMemory(
                organization_id=organization_id,
                column_name_normalized=column_name_normalized,
                original_examples=[column_name_original],
                business_field=business_field,
                physical_type=physical_type,
                confirm_count=1,
                avg_confidence=confidence,
            )
            self.db.add(memory)
