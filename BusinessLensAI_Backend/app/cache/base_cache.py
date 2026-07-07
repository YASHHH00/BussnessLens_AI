"""
BusinessLens AI — Cache Layer: Provider Abstraction

All cache providers implement this interface.
The system functions correctly without any cache (pass-through degradation).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseCacheProvider(ABC):
    """
    Provider-agnostic caching interface.

    The platform never calls Redis/cachetools directly — it always goes
    through this abstraction, making the cache provider swappable without
    touching any business logic.
    """

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """Return the cached value, or None on miss or expiry."""
        ...

    @abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        """Store a value. TTL overrides provider default when supplied."""
        ...

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Remove a specific key."""
        ...

    @abstractmethod
    async def delete_pattern(self, pattern: str) -> int:
        """
        Remove all keys matching a glob pattern.
        Returns the count of deleted keys.
        Use for bulk invalidation (e.g., all cache for a connection).
        """
        ...

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Return True if the key exists and has not expired."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if the cache provider is reachable and operational."""
        ...

    async def get_or_set(
        self,
        key: str,
        factory,
        ttl_seconds: int | None = None,
    ) -> Any:
        """
        Convenience: return cached value or compute + cache it.
        `factory` must be an async callable that returns the value.

        Usage:
            result = await cache.get_or_set(
                key=CacheKeys.kpi_result(conn_id, "total_revenue", date_hash),
                factory=lambda: kpi_engine.compute_kpi(...),
                ttl_seconds=settings.CACHE_KPI_TTL_SECONDS,
            )
        """
        cached = await self.get(key)
        if cached is not None:
            return cached
        value = await factory()
        if value is not None:
            await self.set(key, value, ttl_seconds)
        return value
