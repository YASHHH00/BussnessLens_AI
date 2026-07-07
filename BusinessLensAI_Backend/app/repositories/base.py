"""
BusinessLens AI — BaseRepository with Mandatory Tenant Guard

Every data access operation on tenant-scoped models automatically filters
by organization_id. No per-endpoint discipline required — the guard is
enforced at the repository level, making multi-tenant data leaks impossible
as long as services use the repository pattern.
"""

from __future__ import annotations

from typing import Any, Generic, Type, TypeVar
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base, TenantMixin

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """
    Generic CRUD repository with mandatory multi-tenant isolation.

    The `model_class` attribute must be set on every subclass.
    Every query method that returns tenant data requires organization_id.
    """

    model_class: Type[ModelT]

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def _tenant_guard(self, organization_id: UUID) -> Any:
        """Return the organization_id filter expression for this model."""
        if not hasattr(self.model_class, "organization_id"):
            raise TypeError(
                f"{self.model_class.__name__} does not have an organization_id column. "
                "Use the TenantMixin or query without the tenant guard."
            )
        return self.model_class.organization_id == organization_id

    # ------------------------------------------------------------------ #
    # Create
    # ------------------------------------------------------------------ #

    async def create(self, obj: ModelT) -> ModelT:
        """Persist a new model instance."""
        self.db.add(obj)
        await self.db.flush([obj])
        await self.db.refresh(obj)
        return obj

    async def create_many(self, objects: list[ModelT]) -> list[ModelT]:
        """Persist multiple new instances in a single flush."""
        for obj in objects:
            self.db.add(obj)
        await self.db.flush(objects)
        for obj in objects:
            await self.db.refresh(obj)
        return objects

    # ------------------------------------------------------------------ #
    # Read — tenant-scoped
    # ------------------------------------------------------------------ #

    async def get_by_id(
        self, record_id: UUID, organization_id: UUID
    ) -> ModelT | None:
        """Return a record by PK, scoped to the organization. Returns None if not found."""
        stmt = select(self.model_class).where(
            self.model_class.id == record_id,
            self._tenant_guard(organization_id),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_or_raise(
        self, record_id: UUID, organization_id: UUID, resource_name: str | None = None
    ) -> ModelT:
        """Return a record or raise NotFoundError."""
        from app.core.exceptions import NotFoundError
        obj = await self.get_by_id(record_id, organization_id)
        if obj is None:
            name = resource_name or self.model_class.__name__
            raise NotFoundError(resource=name, resource_id=record_id)
        return obj

    async def list_all(
        self,
        organization_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ModelT]:
        """Return a paginated list of records for the organization."""
        stmt = (
            select(self.model_class)
            .where(self._tenant_guard(organization_id))
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count(self, organization_id: UUID) -> int:
        """Return the total count of records for the organization."""
        from sqlalchemy import func
        stmt = select(func.count()).select_from(self.model_class).where(
            self._tenant_guard(organization_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

    # ------------------------------------------------------------------ #
    # Delete — tenant-scoped
    # ------------------------------------------------------------------ #

    async def delete_by_id(self, record_id: UUID, organization_id: UUID) -> bool:
        """
        Delete a record by PK, scoped to org.
        Returns True if deleted, False if not found.
        """
        stmt = (
            delete(self.model_class)
            .where(
                self.model_class.id == record_id,
                self._tenant_guard(organization_id),
            )
            .returning(self.model_class.id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    # ------------------------------------------------------------------ #
    # Existence check
    # ------------------------------------------------------------------ #

    async def exists(self, record_id: UUID, organization_id: UUID) -> bool:
        """Return True if the record exists and belongs to the org."""
        stmt = select(self.model_class.id).where(
            self.model_class.id == record_id,
            self._tenant_guard(organization_id),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
