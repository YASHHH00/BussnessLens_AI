"""
BusinessLens AI — Cache Factory

Creates the appropriate cache provider based on CACHE_PROVIDER config.
Falls back to in-memory if Redis URL is missing or connection fails.
"""

from __future__ import annotations

from app.cache.base_cache import BaseCacheProvider
from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def create_cache_provider() -> BaseCacheProvider:
    """
    Factory function — creates and returns the configured cache provider.
    Called once during app startup lifespan.
    """
    if settings.CACHE_PROVIDER == "redis" and settings.REDIS_URL:
        try:
            from app.cache.redis_provider import RedisCacheProvider
            provider = RedisCacheProvider(
                redis_url=settings.REDIS_URL,
                default_ttl_seconds=settings.CACHE_DEFAULT_TTL_SECONDS,
            )
            logger.info("Cache provider: Redis (url=%s)", settings.REDIS_URL)
            return provider
        except Exception as exc:
            logger.warning(
                "Failed to initialize Redis cache (%s). Falling back to in-memory.", exc
            )

    # Fallback: in-memory
    from app.cache.memory_provider import MemoryCacheProvider
    provider = MemoryCacheProvider(default_ttl_seconds=settings.CACHE_DEFAULT_TTL_SECONDS)
    logger.info("Cache provider: in-memory (TTL=%ds)", settings.CACHE_DEFAULT_TTL_SECONDS)
    return provider
