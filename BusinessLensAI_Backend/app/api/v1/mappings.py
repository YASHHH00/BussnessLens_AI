"""
BusinessLens AI — Mapping API Router
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_active_plugin, get_cache, get_field_registry
from app.core.database import get_db
from app.schemas.mapping import MappingConfirmRequest, MappingListResponse, MappingSetResponse
from app.services.mapping_service import MappingService

router = APIRouter(prefix="/connections/{connection_id}/mappings", tags=["Mappings"])


def _get_mapping_service(
    db: AsyncSession = Depends(get_db),
    registry=Depends(get_field_registry),
    cache=Depends(get_cache),
) -> MappingService:
    """
    Build MappingService with registered dependencies.
    AI provider is optional — maps degrade to rules-only when unavailable.
    """
    from app.api.deps import _active_plugin
    return MappingService(
        db=db,
        registry=registry,
        ai_provider=None,  # Injected from app deps in Phase 3 integration
        cache=cache,
    )


@router.post("/analyze", response_model=MappingSetResponse, status_code=201)
async def trigger_ai_analysis(
    connection_id: UUID,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
    registry=Depends(get_field_registry),
    cache=Depends(get_cache),
):
    """
    Run AI schema analysis and create a draft MappingSet (status='ai_suggested').
    The user reviews and confirms the mapping via POST /mappings/confirm.
    """
    from app.api import deps

    svc = MappingService(
        db=db,
        registry=registry,
        ai_provider=deps._active_plugin,  # Will be actual AI provider post-refactor
        cache=cache,
    )
    # Use the actual AI provider from the deps module
    import app.api.deps as _deps
    # Rebuild with the actual AI provider singleton (injected at startup)
    ai_provider = getattr(_deps, "_ai_provider", None)
    svc._ai_provider = ai_provider
    svc._optimizer = __import__(
        "app.ai.cost_optimizer", fromlist=["AICostOptimizer"]
    ).AICostOptimizer(provider=ai_provider, cache=cache)

    return await svc.create_from_ai_analysis(
        connection_id=connection_id,
        organization_id=current_user.organization_id,
        user_id=current_user.id,
    )


@router.get("", response_model=MappingListResponse)
async def list_mapping_sets(
    connection_id: UUID,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
    registry=Depends(get_field_registry),
    cache=Depends(get_cache),
):
    """List all MappingSets for a connection (all statuses)."""
    svc = MappingService(db=db, registry=registry, cache=cache)
    sets = await svc.list_mapping_sets(connection_id, current_user.organization_id)
    return MappingListResponse(mapping_sets=sets, total=len(sets))


@router.get("/{mapping_set_id}", response_model=MappingSetResponse)
async def get_mapping_set(
    connection_id: UUID,
    mapping_set_id: UUID,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
    registry=Depends(get_field_registry),
    cache=Depends(get_cache),
):
    """Get a specific MappingSet with all its FieldMappings."""
    svc = MappingService(db=db, registry=registry, cache=cache)
    return await svc.get_mapping_set(mapping_set_id, current_user.organization_id)


@router.get("/{mapping_set_id}/validate")
async def validate_mapping_set(
    connection_id: UUID,
    mapping_set_id: UUID,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
    registry=Depends(get_field_registry),
    cache=Depends(get_cache),
):
    """
    Run all 10 validation rules against a MappingSet without confirming.
    Returns a list of violations (errors + warnings).
    """
    svc = MappingService(db=db, registry=registry, cache=cache)
    return await svc.validate_mapping_set(mapping_set_id, current_user.organization_id)


@router.post("/confirm", response_model=MappingSetResponse)
async def confirm_mapping(
    connection_id: UUID,
    data: MappingConfirmRequest,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
    registry=Depends(get_field_registry),
    cache=Depends(get_cache),
):
    """
    Confirm a MappingSet (optionally with user overrides).

    On confirmation:
    - Previous confirmed sets are archived
    - Smart Mapping Memory is updated
    - SemanticContext cache is invalidated
    - The Semantic Layer will rebuild on next request
    """
    svc = MappingService(db=db, registry=registry, cache=cache)
    return await svc.confirm_mapping_set(
        mapping_set_id=data.mapping_set_id,
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        overrides=data.overrides,
    )
