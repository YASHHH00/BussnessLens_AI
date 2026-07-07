"""
BusinessLens AI — SQL Playground API Router
"""

from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, require_role
from app.core.database import get_db
from app.schemas.sql_playground import SQLPlaygroundRequest, SQLPlaygroundResponse
from app.services.sql_playground_service import SQLPlaygroundService

router = APIRouter(prefix="/connections/{connection_id}/sql-playground", tags=["SQL Playground"])


@router.post(
    "/execute",
    response_model=SQLPlaygroundResponse,
    dependencies=[require_role("data_analyst", "admin")],
)
async def execute_sql_query(
    connection_id: UUID,
    request: SQLPlaygroundRequest,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Execute a read-only SQL query against the connection.
    Strictly role-gated to Data Analysts and Admins.
    Write and DDL statements are rejected by validation engine.
    """
    svc = SQLPlaygroundService(db)
    return await svc.execute_query(connection_id, current_user.organization_id, current_user.id, request)
