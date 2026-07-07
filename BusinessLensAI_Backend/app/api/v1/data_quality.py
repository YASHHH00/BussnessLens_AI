"""
BusinessLens AI — Data Quality API Router
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser
from app.core.database import get_db
from app.schemas.data_quality import DataQualityReportResponse
from app.services.data_quality_service import DataQualityService

router = APIRouter(prefix="/connections/{connection_id}/quality", tags=["Data Quality"])


@router.post("", response_model=DataQualityReportResponse, status_code=201)
async def run_quality_check(
    connection_id: UUID,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Run a data quality evaluation against the latest schema snapshot.
    Returns a scored report with per-table issue details.
    """
    return await DataQualityService(db).run_quality_check(
        connection_id, current_user.organization_id
    )
