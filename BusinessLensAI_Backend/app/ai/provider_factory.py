"""
BusinessLens AI — AI Provider Factory (replaces Phase 1 stub)

Creates the configured AI provider instance. Called once at app startup.
"""

from __future__ import annotations

from app.ai.base_provider import BaseAIProvider
from app.core.config import settings
from app.core.exceptions import AIProviderError
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class ProviderFactory:
    """
    Creates the correct AI provider based on AI_PROVIDER config.
    Returns None gracefully when no API key is configured — AI features
    degrade to cache/rules-only mode (cost optimizer handles this).
    """

    def create(self) -> BaseAIProvider | None:
        provider_name = settings.AI_PROVIDER

        if provider_name == "gemini":
            if not settings.GEMINI_API_KEY:
                logger.warning(
                    "GEMINI_API_KEY not set — AI features will be unavailable. "
                    "The platform will use rules engine and cached data only."
                )
                return None
            from app.ai.gemini_provider import GeminiProvider
            provider = GeminiProvider(api_key=settings.GEMINI_API_KEY)
            logger.info("AI provider initialized: Gemini (%s)", provider.model_name)
            return provider

        if provider_name == "openai":
            if not settings.OPENAI_API_KEY:
                logger.warning(
                    "OPENAI_API_KEY not set — AI features will be unavailable."
                )
                return None
            from app.ai.openai_provider import OpenAIProvider
            provider = OpenAIProvider(api_key=settings.OPENAI_API_KEY)
            logger.info("AI provider initialized: OpenAI (%s)", provider.model_name)
            return provider

        raise AIProviderError(
            provider_name,
            f"Unknown AI provider '{provider_name}'. Valid options: gemini, openai",
        )
