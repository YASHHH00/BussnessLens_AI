"""
BusinessLens AI — Insight Engine

Converts deterministic analytics outputs (KPIs & rule triggers) into executive-level
natural language narrative and actionable recommendations using AI.
Strictly JSON-only output — no SQL generated.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from app.ai.base_provider import AIRequest, BaseAIProvider
from app.ai.cost_optimizer import AICostOptimizer
from app.ai.prompts.prompt_templates import INSIGHT_PHRASING_SYSTEM, build_insight_phrasing_prompt
from app.cache.base_cache import BaseCacheProvider
from app.core.logging_config import get_logger
from app.schemas.analytics import KPIEvaluationResult, RuleTriggerAlert
from app.schemas.insights import InsightGenerationResponse, InsightItem

logger = get_logger(__name__)


class InsightEngine:
    def __init__(
        self,
        ai_provider: BaseAIProvider | None = None,
        cache: BaseCacheProvider | None = None,
    ) -> None:
        self._optimizer = AICostOptimizer(provider=ai_provider, cache=cache)

    async def generate_insights(
        self,
        connection_id: UUID,
        kpi_results: list[KPIEvaluationResult],
        rule_alerts: list[RuleTriggerAlert],
        domain_name: str = "retail",
        date_range: str = "Current Period",
    ) -> InsightGenerationResponse:
        """
        Synthesize executive insights from KPI values and triggered rules.
        Uses cost optimizer caching (keyed on inputs hash).
        """
        kpi_dicts = [k.model_dump() for k in kpi_results]
        rule_dicts = [r.model_dump() for r in rule_alerts]
        domain_ctx = {"domain": domain_name}

        prompt = build_insight_phrasing_prompt(
            kpi_results=kpi_dicts,
            rule_triggers=rule_dicts,
            domain_context=domain_ctx,
            date_range=date_range,
        )

        import hashlib, json
        input_str = json.dumps({"k": kpi_dicts, "r": rule_dicts}, sort_keys=True)
        h = hashlib.sha256(input_str.encode()).hexdigest()[:16]
        cache_key = f"biz:insights:{connection_id}:{h}"

        request = AIRequest(
            prompt=prompt,
            system_instruction=INSIGHT_PHRASING_SYSTEM,
            temperature=0.2,
            max_output_tokens=4096,
            response_format="json",
        )

        response = await self._optimizer.complete(request=request, cache_key=cache_key)
        raw = response.parse_json()

        items = []
        for raw_item in raw.get("insights", []):
            items.append(
                InsightItem(
                    title=raw_item.get("title", "Key Finding"),
                    body=raw_item.get("body", ""),
                    severity=raw_item.get("severity", "info"),
                    metric=raw_item.get("metric", "General"),
                    recommended_action=raw_item.get("recommended_action"),
                    confidence=float(raw_item.get("confidence", 0.9)),
                )
            )

        return InsightGenerationResponse(
            executive_summary=raw.get("executive_summary", "Review the period performance and key rule alerts below."),
            insights=items,
            generated_at=datetime.now(UTC),
            provider=response.provider,
            model=response.model,
            tokens_used=response.total_tokens,
        )
