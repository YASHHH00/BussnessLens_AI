"""
BusinessLens AI — Redis Cache Provider (Production)

Uses redis.asyncio with JSON serialization, SCAN-based pattern deletion,
and graceful degradation on connection failure.
"""

from __future__ import annotations

import json
from typing import Any

from app.cache.base_cache import BaseCacheProvider
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class RedisCacheProvider(BaseCacheProvider):
    """
    Redis-backed cache provider for production environments.

    Features:
    - Async via redis.asyncio
    - JSON serialization
    - SCAN-based pattern deletion (never KEYS * in production)
    - Graceful degradation: Redis errors return cache misses, never crash requests
    """

    def __init__(self, redis_url: str, default_ttl_seconds: int = 300) -> None:
        self._redis_url = redis_url
        self._default_ttl = default_ttl_seconds
        self._client = None

    async def _get_client(self):
        """Lazy-initialize the Redis client on first use."""
        if self._client is None:
            try:
                import redis.asyncio as aioredis
                self._client = aioredis.from_url(
                    self._redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                )
            except Exception as exc:
                logger.error("Failed to create Redis client: %s", exc)
                raise
        return self._client

    async def get(self, key: str) -> Any | None:
        try:
            client = await self._get_client()
            raw = await client.get(key)
            if raw is None:
                return None
            return json.loads(raw)
        except Exception as exc:
            logger.warning("Redis get failed for key=%s: %s — cache miss", key, exc)
            return None

    async def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        try:
            client = await self._get_client()
            ttl = ttl_seconds if ttl_seconds is not None else self._default_ttl
            await client.setex(key, ttl, json.dumps(value, default=str))
        except Exception as exc:
            logger.warning("Redis set failed for key=%s: %s", key, exc)

    async def delete(self, key: str) -> None:
        try:
            client = await self._get_client()
            await client.delete(key)
        except Exception as exc:
            logger.warning("Redis delete failed for key=%s: %s", key, exc)

    async def delete_pattern(self, pattern: str) -> int:
        """
        SCAN + DELETE — safe for production (never KEYS *).
        Returns the number of keys deleted.
        """
        deleted = 0
        try:
            client = await self._get_client()
            cursor = 0
            while True:
                cursor, keys = await client.scan(cursor=cursor, match=pattern, count=100)
                if keys:
                    await client.delete(*keys)
                    deleted += len(keys)
                if cursor == 0:
                    break
        except Exception as exc:
            logger.warning("Redis delete_pattern failed for pattern=%s: %s", pattern, exc)
        return deleted

    async def exists(self, key: str) -> bool:
        try:
            client = await self._get_client()
            return bool(await client.exists(key))
        except Exception:
            return False

    async def health_check(self) -> bool:
        try:
            client = await self._get_client()
            return await client.ping()
        except Exception:
            return False

    async def close(self) -> None:
        """Close the Redis connection pool. Call during app shutdown."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def __repr__(self) -> str:
        return f"<RedisCacheProvider url={self._redis_url}>"
