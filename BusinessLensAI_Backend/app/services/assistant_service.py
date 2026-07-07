"""
BusinessLens AI — Assistant Service
"""

from __future__ import annotations

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.base_cache import BaseCacheProvider
from app.engines.assistant_engine import AssistantEngine
from app.registry.field_registry import BusinessFieldRegistry
from app.schemas.assistant import AssistantChatRequest, AssistantChatResponse
from app.services.analytics_service import AnalyticsService


class AssistantService:
    def __init__(
        self,
        db: AsyncSession,
        registry: BusinessFieldRegistry,
        ai_provider=None,
        cache: BaseCacheProvider | None = None,
    ) -> None:
        self._analytics_svc = AnalyticsService(db, registry, cache)
        self._engine = AssistantEngine(registry=registry, ai_provider=ai_provider, cache=cache)

    async def handle_message(
        self,
        connection_id: UUID,
        organization_id: UUID,
        request: AssistantChatRequest,
    ) -> AssistantChatResponse:
        kpis = await self._analytics_svc.evaluate_kpis(connection_id, organization_id)
        kpi_summary = [
            {"name": k.display_name, "val": k.formatted_value} for k in kpis
        ]

        resp = await self._engine.chat(
            connection_id=connection_id,
            request=request,
            recent_kpis=kpi_summary,
            history=[],
        )

        if resp.suggested_query and request.execute_suggested_query:
            try:
                res = await self._analytics_svc.execute_query(
                    connection_id=connection_id,
                    organization_id=organization_id,
                    request=resp.suggested_query,
                )
                resp.query_result = res
            except Exception:
                pass

        return resp
