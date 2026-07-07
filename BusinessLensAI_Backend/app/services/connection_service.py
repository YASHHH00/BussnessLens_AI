"""
BusinessLens AI — Connection Service

Handles: create, test, list, delete connections with SSRF protection and Fernet encryption.
"""

from __future__ import annotations

import time
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.connectors.connector_factory import ConnectorFactory
from app.core.audit import AuditAction, emit_audit_log
from app.core.exceptions import ConflictError, NotFoundError
from app.core.security import encrypt_credential
from app.models.connection import (
    DBConnection,
    ConnectionType,
    PLANNED_CONNECTOR_TYPES,
    SUPPORTED_CONNECTOR_TYPES,
)
from app.repositories.connection_repository import ConnectionRepository
from app.schemas.connection import (
    ConnectionCreateRequest,
    ConnectionResponse,
    ConnectionTestRequest,
    ConnectionTestResult,
)
from app.utils.ssrf_guard import validate_host


class ConnectionService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = ConnectionRepository(db)
        self._db = db
        self._factory = ConnectorFactory()

    async def test_connection(
        self,
        data: ConnectionTestRequest,
        ip_address: str | None = None,
    ) -> ConnectionTestResult:
        """Test a connection WITHOUT saving it. SSRF guard applied first."""
        if data.host:
            validate_host(data.host, data.port)

        t0 = time.monotonic()
        connector = self._factory.create_from_params(
            connection_type=data.connection_type,
            host=data.host,
            port=data.port,
            database=data.database,
            username=data.username,
            password=data.password,
            ssl=data.ssl_enabled,
        )
        await connector.test_connection()
        latency_ms = int((time.monotonic() - t0) * 1000)
        await connector.close()
        return ConnectionTestResult(
            success=True,
            message="Connection successful.",
            latency_ms=latency_ms,
        )

    async def create_connection(
        self,
        data: ConnectionCreateRequest,
        user_id: UUID,
        organization_id: UUID,
        ip_address: str | None = None,
    ) -> ConnectionResponse:
        """Create and persist a new connection. Password is Fernet-encrypted."""
        # Duplicate name check
        existing = await self._repo.get_by_name(data.name, organization_id)
        if existing:
            raise ConflictError(
                f"A connection named '{data.name}' already exists."
            )

        # SSRF guard for DB connections
        if data.host:
            validate_host(data.host, data.port)

        # Encrypt password
        encrypted_pw = None
        if data.password:
            encrypted_pw = encrypt_credential(data.password)

        conn = DBConnection(
            name=data.name,
            description=data.description,
            connection_type=data.connection_type,
            host=data.host,
            port=data.port,
            database=data.database,
            username=data.username,
            encrypted_password=encrypted_pw,
            ssl_enabled=data.ssl_enabled,
            extra_params=data.extra_params,
            organization_id=organization_id,
            created_by=user_id,
        )
        conn = await self._repo.create(conn)

        await emit_audit_log(
            db=self._db,
            action=AuditAction.CONNECTION_CREATED,
            user_id=user_id,
            organization_id=organization_id,
            resource_type="connection",
            resource_id=conn.id,
            details={"name": conn.name, "type": conn.connection_type},
            ip_address=ip_address,
        )

        return ConnectionResponse.model_validate(conn)

    async def get_connection(
        self, connection_id: UUID, organization_id: UUID
    ) -> ConnectionResponse:
        conn = await self._repo.get_by_id_or_raise(connection_id, organization_id, "Connection")
        return ConnectionResponse.model_validate(conn)

    async def list_connections(
        self, organization_id: UUID, limit: int = 50, offset: int = 0
    ) -> list[ConnectionResponse]:
        connections = await self._repo.list_all(organization_id, limit=limit, offset=offset)
        return [ConnectionResponse.model_validate(c) for c in connections]

    async def delete_connection(
        self, connection_id: UUID, organization_id: UUID, user_id: UUID
    ) -> None:
        deleted = await self._repo.delete_by_id(connection_id, organization_id)
        if not deleted:
            raise NotFoundError("Connection", connection_id)

        await emit_audit_log(
            db=self._db,
            action=AuditAction.CONNECTION_DELETED,
            user_id=user_id,
            organization_id=organization_id,
            resource_type="connection",
            resource_id=connection_id,
        )
