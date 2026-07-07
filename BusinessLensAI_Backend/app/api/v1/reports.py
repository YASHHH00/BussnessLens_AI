"""
BusinessLens AI — Report Export API Router
"""

from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_field_registry
from app.core.database import get_db
from app.schemas.reports import ReportExportRequest
from app.services.report_service import ReportService

router = APIRouter(prefix="/connections/{connection_id}/reports", tags=["Report Generation"])


@router.post("/export")
async def export_report(
    connection_id: UUID,
    request: ReportExportRequest,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
    registry=Depends(get_field_registry),
):
    """
    Generate and download an executive spreadsheet report (.xlsx)
    containing KPIs and underlying detailed metric rows.
    """
    svc = ReportService(db=db, registry=registry)
    content = await svc.export_excel(connection_id, current_user.organization_id, current_user.id, request)

    headers = {
        "Content-Disposition": f'attachment; filename="{request.title.replace(" ", "_")}.xlsx"'
    }
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )
