"""
BusinessLens AI — Admin Service
"""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.base_cache import BaseCacheProvider
from app.schemas.admin import AICostStatsResponse, SystemHealthResponse


class AdminService:
    def __init__(self, db: AsyncSession, ai_provider=None, cache: BaseCacheProvider | None = None) -> None:
        self._db = db
        self._ai_provider = ai_provider
        self._cache = cache

    async def get_ai_stats(self) -> list[AICostStatsResponse]:
        if not self._ai_provider:
            return [
                AICostStatsResponse(
                    provider="none",
                    total_calls=0,
                    total_tokens=0,
                    cache_hits=0,
                    estimated_cost_usd=0.0,
                )
            ]

        # Return usage stats from ai_provider object if available
        calls = getattr(self._ai_provider, "total_calls", 0)
        tokens = getattr(self._ai_provider, "total_tokens", 0)
        cost = getattr(self._ai_provider, "estimated_cost_usd", 0.0)

        return [
            AICostStatsResponse(
                provider=getattr(self._ai_provider, "provider_name", "gemini"),
                total_calls=calls,
                total_tokens=tokens,
                cache_hits=0,
                estimated_cost_usd=round(cost, 6),
            )
        ]

    async def get_system_health(self) -> SystemHealthResponse:
        db_ok = False
        try:
            await self._db.execute(text("SELECT 1"))
            db_ok = True
        except Exception:
            pass

        cache_keys = 0
        if self._cache and hasattr(self._cache, "client"):
            try:
                # count redis keys
                pass
            except Exception:
                pass

        status_str = "healthy" if db_ok else "degraded"
        return SystemHealthResponse(
            status=status_str,
            db_connection=db_ok,
            active_connections_count=1,
            cached_queries_count=cache_keys,
            details={"version": "v1.0.0", "engine": "asyncio-fastapi"},
        )
