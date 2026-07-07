"""
BusinessLens AI — AI Assistant API Router
"""

from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.api.deps import CurrentUser, get_cache, get_field_registry
from app.core.database import get_db
from app.schemas.assistant import AssistantChatRequest, AssistantChatResponse
from app.services.assistant_service import AssistantService

router = APIRouter(prefix="/connections/{connection_id}/assistant", tags=["AI Business Assistant"])


@router.post("/chat", response_model=AssistantChatResponse)
async def chat_with_assistant(
    connection_id: UUID,
    request: AssistantChatRequest,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
    registry=Depends(get_field_registry),
    cache=Depends(get_cache),
):
    """Chat with the AI Business Assistant over the connection's data and schema."""
    ai_provider = getattr(deps, "_ai_provider", None)
    svc = AssistantService(db=db, registry=registry, ai_provider=ai_provider, cache=cache)
    return await svc.handle_message(connection_id, current_user.organization_id, request)
