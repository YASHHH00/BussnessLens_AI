"""
BusinessLens AI — Semantic Layer API Router
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_cache, require_role
from app.core.database import get_db
from app.schemas.common import MessageResponse
from app.services.semantic_service import SemanticService

router = APIRouter(prefix="/connections/{connection_id}/semantic", tags=["Semantic Layer"])


@router.get("/context")
async def get_semantic_context(
    connection_id: UUID,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
    cache=Depends(get_cache),
):
    """
    Return the SemanticContext summary for a connection.
    Shows mapped business fields, tables, and join paths.
    Requires a confirmed MappingSet.
    """
    svc = SemanticService(db=db, cache=cache)
    return await svc.get_context_summary(connection_id, current_user.organization_id)


@router.get("/context/full", dependencies=[require_role("data_analyst", "admin")])
async def get_full_semantic_context(
    connection_id: UUID,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
    cache=Depends(get_cache),
):
    """
    Return the full SemanticContext including all column-level details.
    Restricted to Data Analyst and Admin roles.
    """
    svc = SemanticService(db=db, cache=cache)
    return await svc.get_full_context(connection_id, current_user.organization_id)


@router.post("/invalidate", response_model=MessageResponse,
             dependencies=[require_role("data_analyst", "admin")])
async def invalidate_semantic_cache(
    connection_id: UUID,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
    cache=Depends(get_cache),
):
    """
    Manually invalidate the cached SemanticContext for a connection.
    The context will be rebuilt from DB on the next request.
    Restricted to Data Analyst and Admin roles.
    """
    svc = SemanticService(db=db, cache=cache)
    await svc.invalidate(connection_id)
    return MessageResponse(message="Semantic context cache cleared successfully.")
