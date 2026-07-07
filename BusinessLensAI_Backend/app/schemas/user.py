"""
BusinessLens AI — Pydantic Schemas: User
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    role: str
    organization_id: UUID
    is_active: bool
    theme_preference: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=1, max_length=256)
    theme_preference: str | None = Field(None, pattern="^(dark|light|system)$")


class UserCreate(BaseModel):
    """Admin-only: create a user with a specific role."""
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=1, max_length=256)
    role: str = "business_analyst"


class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int


class ThemePreferenceUpdate(BaseModel):
    theme: str = Field(pattern="^(dark|light|system)$")
