"""
BusinessLens AI — SQL Playground Service
"""

from __future__ import annotations

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.connectors.connector_factory import ConnectorFactory
from app.core.audit import AuditAction, emit_audit_log
from app.engines.sql_playground_engine import SQLPlaygroundEngine
from app.repositories.connection_repository import ConnectionRepository
from app.schemas.sql_playground import SQLPlaygroundRequest, SQLPlaygroundResponse


class SQLPlaygroundService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._conn_repo = ConnectionRepository(db)
        self._engine = SQLPlaygroundEngine()
        self._factory = ConnectorFactory()

    async def execute_query(
        self,
        connection_id: UUID,
        organization_id: UUID,
        user_id: UUID,
        request: SQLPlaygroundRequest,
    ) -> SQLPlaygroundResponse:
        conn = await self._conn_repo.get_by_id_or_raise(connection_id, organization_id, "Connection")
        connector = self._factory.create_from_model(conn)

        result = await self._engine.execute_readonly(connector, request.query, request.limit)

        await emit_audit_log(
            db=self._db,
            action=AuditAction.SQL_PLAYGROUND_EXECUTED,
            user_id=user_id,
            organization_id=organization_id,
            resource_type="connection",
            resource_id=connection_id,
            details={"rows_returned": result.total_rows, "execution_time_ms": result.execution_time_ms},
        )

        return result
