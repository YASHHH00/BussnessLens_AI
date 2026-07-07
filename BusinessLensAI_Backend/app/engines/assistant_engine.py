"""
BusinessLens AI — Assistant Engine

Conversational interface translating natural language questions into structured queries
or executive narrative answers over semantic metrics.
Strictly JSON outputs — no SQL generated.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.ai.base_provider import AIRequest, BaseAIProvider
from app.ai.cost_optimizer import AICostOptimizer
from app.ai.prompts.prompt_templates import ASSISTANT_SYSTEM, build_assistant_prompt
from app.cache.base_cache import BaseCacheProvider
from app.core.logging_config import get_logger
from app.registry.field_registry import BusinessFieldRegistry
from app.schemas.analytics import AnalyticsQueryRequest
from app.schemas.assistant import AssistantChatRequest, AssistantChatResponse

logger = get_logger(__name__)


class AssistantEngine:
    def __init__(
        self,
        registry: BusinessFieldRegistry,
        ai_provider: BaseAIProvider | None = None,
        cache: BaseCacheProvider | None = None,
    ) -> None:
        self._registry = registry
        self._optimizer = AICostOptimizer(provider=ai_provider, cache=cache)

    async def chat(
        self,
        connection_id: UUID,
        request: AssistantChatRequest,
        recent_kpis: list[dict],
        history: list[dict],
    ) -> AssistantChatResponse:
        vocab = self._registry.get_vocabulary_for_prompt()
        prompt = build_assistant_prompt(
            question=request.message,
            field_vocabulary=vocab,
            recent_kpi_summary=recent_kpis,
            conversation_history=history,
        )

        ai_req = AIRequest(
            prompt=prompt,
            system_instruction=ASSISTANT_SYSTEM,
            temperature=0.2,
            max_output_tokens=2048,
            response_format="json",
        )

        response = await self._optimizer.complete(request=ai_req)
        raw = response.parse_json()

        intent = raw.get("intent", "answer")
        narrative = raw.get("narrative_response", "I processed your question against our active schema.")
        sug_query_dict = raw.get("suggested_query")

        suggested_query: AnalyticsQueryRequest | None = None
        if sug_query_dict and isinstance(sug_query_dict, dict) and sug_query_dict.get("metrics"):
            try:
                suggested_query = AnalyticsQueryRequest.model_validate(sug_query_dict)
            except Exception as exc:
                logger.warning("Could not parse AI suggested query: %s", exc)

        follow_ups = raw.get("follow_up_questions", [])
        if not isinstance(follow_ups, list):
            follow_ups = []

        return AssistantChatResponse(
            thread_id=request.thread_id or uuid4(),
            intent=intent,
            narrative=narrative,
            suggested_query=suggested_query,
            query_result=None,
            follow_up_questions=follow_ups,
            created_at=datetime.now(UTC),
        )
