"""
BusinessLens AI — Dashboards API Router
"""

from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser
from app.core.database import get_db
from app.schemas.common import MessageResponse
from app.schemas.dashboard import DashboardCreateRequest, DashboardListResponse, DashboardResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/connections/{connection_id}/dashboards", tags=["Dashboards"])


@router.get("", response_model=DashboardListResponse)
async def list_dashboards(
    connection_id: UUID,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """List all dashboards for a connection."""
    svc = DashboardService(db)
    items = await svc.list_dashboards(connection_id, current_user.organization_id)
    return DashboardListResponse(dashboards=items, total=len(items))


@router.post("/auto-generate", response_model=list[DashboardResponse], status_code=status.HTTP_201_CREATED)
async def auto_generate_dashboards(
    connection_id: UUID,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Auto-generate default dashboards based on domain templates and mapped fields.
    """
    svc = DashboardService(db)
    return await svc.auto_generate_dashboards(connection_id, current_user.organization_id, current_user.id)


@router.post("", response_model=DashboardResponse, status_code=status.HTTP_201_CREATED)
async def create_custom_dashboard(
    connection_id: UUID,
    req: DashboardCreateRequest,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """Create a custom dashboard with widgets."""
    svc = DashboardService(db)
    return await svc.create_dashboard(connection_id, current_user.organization_id, current_user.id, req)


@router.get("/{dashboard_id}", response_model=DashboardResponse)
async def get_dashboard(
    connection_id: UUID,
    dashboard_id: UUID,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific dashboard and its widgets."""
    svc = DashboardService(db)
    return await svc.get_dashboard(dashboard_id, current_user.organization_id)


@router.delete("/{dashboard_id}", response_model=MessageResponse)
async def delete_dashboard(
    connection_id: UUID,
    dashboard_id: UUID,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """Delete a dashboard."""
    svc = DashboardService(db)
    await svc.delete_dashboard(dashboard_id, current_user.organization_id, current_user.id)
    return MessageResponse(message="Dashboard deleted successfully.")
