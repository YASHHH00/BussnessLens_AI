"""
BusinessLens AI — Pydantic Schemas: Common / Shared
"""

from __future__ import annotations

from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorResponse(BaseModel):
    error_code: str
    message: str
    details: dict | None = None


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=200)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int

    @classmethod
    def build(cls, items: list[T], total: int, pagination: PaginationParams):
        import math
        return cls(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            pages=math.ceil(total / pagination.page_size) if total > 0 else 0,
        )


class JobStatusResponse(BaseModel):
    job_id: UUID
    status: str
    progress_message: str | None = None
    result_data: dict | None = None
    error_message: str | None = None

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    message: str
