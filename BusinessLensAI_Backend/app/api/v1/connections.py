"""
BusinessLens AI — Connections API Router
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser
from app.core.database import get_db
from app.schemas.common import MessageResponse
from app.schemas.connection import (
    ConnectionCreateRequest,
    ConnectionListResponse,
    ConnectionResponse,
    ConnectionTestRequest,
    ConnectionTestResult,
)
from app.services.connection_service import ConnectionService

router = APIRouter(prefix="/connections", tags=["Connections"])


@router.post("/test", response_model=ConnectionTestResult)
async def test_connection(
    data: ConnectionTestRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None,
):
    """Test a database connection without saving it. SSRF-protected."""
    ip = request.client.host if request.client else None
    return await ConnectionService(db).test_connection(data, ip_address=ip)


@router.post("", response_model=ConnectionResponse, status_code=201)
async def create_connection(
    data: ConnectionCreateRequest,
    request: Request,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """Create a new database or file connection. Password is encrypted at rest."""
    ip = request.client.host if request.client else None
    return await ConnectionService(db).create_connection(
        data,
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        ip_address=ip,
    )


@router.get("", response_model=ConnectionListResponse)
async def list_connections(
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
):
    """List all connections for the current organization."""
    connections = await ConnectionService(db).list_connections(
        current_user.organization_id, limit=limit, offset=offset
    )
    return ConnectionListResponse(connections=connections, total=len(connections))


@router.get("/{connection_id}", response_model=ConnectionResponse)
async def get_connection(
    connection_id: UUID,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """Get a single connection by ID."""
    return await ConnectionService(db).get_connection(connection_id, current_user.organization_id)


@router.delete("/{connection_id}", response_model=MessageResponse)
async def delete_connection(
    connection_id: UUID,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """Delete a connection (and all associated scans)."""
    await ConnectionService(db).delete_connection(
        connection_id, current_user.organization_id, current_user.id
    )
    return MessageResponse(message="Connection deleted successfully.")
