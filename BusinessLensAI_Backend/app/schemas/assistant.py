"""
BusinessLens AI — AI Assistant Schemas
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from app.schemas.analytics import AnalyticsQueryRequest, AnalyticsQueryResult


class AssistantChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2048)
    thread_id: UUID | None = None
    execute_suggested_query: bool = Field(True, description="Automatically run suggested query if AI converts question to query")


class AssistantChatResponse(BaseModel):
    thread_id: UUID
    intent: str  # answer, query, clarification
    narrative: str
    suggested_query: AnalyticsQueryRequest | None = None
    query_result: AnalyticsQueryResult | None = None
    follow_up_questions: list[str] = Field(default_factory=list)
    created_at: datetime
