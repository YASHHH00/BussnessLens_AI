"""
BusinessLens AI — Connection ORM Model

Stores user-defined database connections.
Credentials are encrypted at rest using Fernet.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, TenantMixin, generate_uuid


class ConnectionType(str):
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MSSQL = "mssql"
    ORACLE = "oracle"
    SQLITE = "sqlite"
    CSV = "csv"
    EXCEL = "excel"


SUPPORTED_CONNECTOR_TYPES: frozenset[str] = frozenset({
    ConnectionType.POSTGRESQL,
    ConnectionType.CSV,
    ConnectionType.EXCEL,
})

PLANNED_CONNECTOR_TYPES: frozenset[str] = frozenset({
    ConnectionType.MYSQL,
    ConnectionType.MSSQL,
    ConnectionType.ORACLE,
    ConnectionType.SQLITE,
})


class DBConnection(Base, TenantMixin, TimestampMixin):
    """
    Stores a database or file connection configuration.

    Security:
    - `encrypted_password` stores the Fernet-encrypted password. Never store plaintext.
    - `connection_string_encrypted` stores a full DSN for file-based sources.
    - `last_tested_at` tracks connection health.
    - `schema_version_hash` detects schema drift between scans.
    """

    __tablename__ = "db_connections"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    # Connection type
    connection_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)

    # DB connection params (for db connectors)
    host: Mapped[str | None] = mapped_column(String(512), nullable=True)
    port: Mapped[int | None] = mapped_column(Integer, nullable=True)
    database: Mapped[str | None] = mapped_column(String(256), nullable=True)
    username: Mapped[str | None] = mapped_column(String(256), nullable=True)
    encrypted_password: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    ssl_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # File-based sources (CSV, Excel)
    file_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    # Connection health
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_tested_at: Mapped[str | None] = mapped_column(String(64), nullable=True)  # ISO string
    last_test_succeeded: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # Schema change tracking
    schema_version_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Extra connection options (e.g. SSH tunnel, custom params)
    extra_params: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict
    )

    created_by: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)

    def __repr__(self) -> str:
        return f"<DBConnection name={self.name} type={self.connection_type}>"
