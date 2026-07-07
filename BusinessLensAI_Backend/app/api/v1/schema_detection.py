"""
BusinessLens AI — Schema Detection API Router
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser
from app.core.database import get_db
from app.schemas.schema_detection import SchemaDriftResponse, SchemaSnapshotResponse
from app.services.schema_detection_service import SchemaDetectionService

router = APIRouter(prefix="/connections/{connection_id}/schema", tags=["Schema Detection"])


@router.post("/scan", status_code=202)
async def trigger_schema_scan(
    connection_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger an async schema scan.
    Returns immediately with a job_id. Poll /jobs/{job_id} for status.
    """
    from app.core.database import db_session

    async def _run_scan():
        async with db_session() as bg_db:
            svc = SchemaDetectionService(bg_db)
            await svc.run_schema_scan(
                connection_id=connection_id,
                organization_id=current_user.organization_id,
                user_id=current_user.id,
            )

    background_tasks.add_task(_run_scan)
    return {"status": "accepted", "message": "Schema scan started."}


@router.get("/latest", response_model=SchemaSnapshotResponse)
async def get_latest_schema(
    connection_id: UUID,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """Return the most recent schema snapshot for a connection."""
    return await SchemaDetectionService(db).get_latest_snapshot(
        connection_id, current_user.organization_id
    )


@router.get("/diff", response_model=SchemaDriftResponse)
async def get_schema_diff(
    connection_id: UUID,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """Compare the two most recent schema snapshots to detect drift."""
    return await SchemaDetectionService(db).get_schema_diff(
        connection_id, current_user.organization_id
    )
