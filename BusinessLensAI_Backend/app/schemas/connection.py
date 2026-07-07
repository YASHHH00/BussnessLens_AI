"""
BusinessLens AI — Pydantic Schemas: Connection
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ConnectionCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=256)
    description: str | None = Field(None, max_length=1024)
    connection_type: str

    # DB connection params
    host: str | None = None
    port: int | None = Field(None, ge=1, le=65535)
    database: str | None = None
    username: str | None = None
    password: str | None = None     # Plaintext — encrypted before storage
    ssl_enabled: bool = False
    extra_params: dict[str, Any] = Field(default_factory=dict)


class ConnectionTestRequest(BaseModel):
    """Test a connection WITHOUT saving it first."""
    connection_type: str
    host: str | None = None
    port: int | None = Field(None, ge=1, le=65535)
    database: str | None = None
    username: str | None = None
    password: str | None = None
    ssl_enabled: bool = False


class ConnectionTestResult(BaseModel):
    success: bool
    message: str
    latency_ms: int | None = None


class ConnectionResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    connection_type: str
    host: str | None
    port: int | None
    database: str | None
    username: str | None
    ssl_enabled: bool
    is_active: bool
    last_tested_at: str | None
    last_test_succeeded: bool | None
    schema_version_hash: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConnectionListResponse(BaseModel):
    connections: list[ConnectionResponse]
    total: int
