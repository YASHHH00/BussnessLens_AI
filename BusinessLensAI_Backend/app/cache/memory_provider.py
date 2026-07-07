"""
BusinessLens AI — In-Memory Cache Provider (Development / Fallback)

Uses cachetools.TTLCache. No external dependency.
Automatically used when CACHE_PROVIDER=memory or when Redis is unavailable.
"""

from __future__ import annotations

import fnmatch
import json
from typing import Any

from cachetools import TTLCache

from app.cache.base_cache import BaseCacheProvider
from app.core.logging_config import get_logger

logger = get_logger(__name__)

_DEFAULT_MAXSIZE = 1024  # Maximum number of cached items


class MemoryCacheProvider(BaseCacheProvider):
    """
    In-memory TTL cache backed by cachetools.TTLCache.

    Suitable for local development and single-process deployments.
    Not shared across multiple workers — use Redis for multi-process setups.
    """

    def __init__(self, default_ttl_seconds: int = 300, maxsize: int = _DEFAULT_MAXSIZE) -> None:
        self._default_ttl = default_ttl_seconds
        # TTLCache evicts entries after their TTL expires
        self._cache: TTLCache = TTLCache(maxsize=maxsize, ttl=default_ttl_seconds)

    def _serialize(self, value: Any) -> str:
        return json.dumps(value, default=str)

    def _deserialize(self, raw: str) -> Any:
        return json.loads(raw)

    async def get(self, key: str) -> Any | None:
        try:
            raw = self._cache.get(key)
            if raw is None:
                return None
            return self._deserialize(raw)
        except Exception:
            logger.warning("Memory cache get failed for key=%s", key)
            return None

    async def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        try:
            # cachetools TTLCache uses a single TTL for the whole cache.
            # For per-key TTL we simply store and rely on the global TTL.
            # Fine for our use case — each cache instance has a specific purpose.
            self._cache[key] = self._serialize(value)
        except Exception:
            logger.warning("Memory cache set failed for key=%s", key)

    async def delete(self, key: str) -> None:
        self._cache.pop(key, None)

    async def delete_pattern(self, pattern: str) -> int:
        matching_keys = [k for k in list(self._cache.keys()) if fnmatch.fnmatch(k, pattern)]
        for key in matching_keys:
            self._cache.pop(key, None)
        return len(matching_keys)

    async def exists(self, key: str) -> bool:
        return key in self._cache

    async def health_check(self) -> bool:
        return True  # In-memory is always available

    def __repr__(self) -> str:
        return f"<MemoryCacheProvider size={len(self._cache)}/{self._cache.maxsize}>"
