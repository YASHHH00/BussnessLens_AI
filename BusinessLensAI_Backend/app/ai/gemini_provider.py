"""
BusinessLens AI — Gemini AI Provider (google-genai SDK)

Uses gemini-2.0-flash for fast, cost-effective schema analysis and mapping suggestions.
All prompts are structured JSON requests — the provider never generates SQL.
"""

from __future__ import annotations

import time
from typing import Any

from app.ai.base_provider import AIRequest, AIResponse, BaseAIProvider
from app.core.config import settings
from app.core.exceptions import AIProviderError
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Pricing as of 2025 (per 1M tokens, USD)
_INPUT_COST_PER_1M = 0.10   # gemini-2.0-flash
_OUTPUT_COST_PER_1M = 0.40


class GeminiProvider(BaseAIProvider):
    """
    Google Gemini provider via the google-genai SDK.

    Model: gemini-2.0-flash
    - Fast, cheap, sufficient for schema analysis and mapping
    - JSON mode enforced for structured outputs
    """

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from google import genai
                self._client = genai.Client(api_key=self._api_key)
            except Exception as exc:
                raise AIProviderError("gemini", f"Failed to init client: {exc}") from exc
        return self._client

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return "gemini-2.0-flash"

    async def complete(self, request: AIRequest) -> AIResponse:
        """
        Send a prompt to Gemini with retry logic.
        JSON mode is requested via response_mime_type when format="json".
        """
        client = self._get_client()
        last_exc: Exception | None = None

        for attempt in range(1, settings.AI_MAX_RETRIES + 2):
            try:
                t0 = time.monotonic()

                from google.genai import types

                # Build contents
                contents = []
                if request.system_instruction:
                    contents.append(
                        types.Content(
                            role="user",
                            parts=[types.Part(text=request.system_instruction)],
                        )
                    )
                contents.append(
                    types.Content(
                        role="user",
                        parts=[types.Part(text=request.prompt)],
                    )
                )

                generate_config = types.GenerateContentConfig(
                    temperature=request.temperature,
                    max_output_tokens=request.max_output_tokens,
                    response_mime_type=(
                        "application/json"
                        if request.response_format == "json"
                        else "text/plain"
                    ),
                )

                response = client.models.generate_content(
                    model=self.model_name,
                    contents=contents,
                    config=generate_config,
                )

                latency_ms = int((time.monotonic() - t0) * 1000)
                text = response.text or ""

                # Token usage
                usage = response.usage_metadata
                input_tokens = getattr(usage, "prompt_token_count", 0) or 0
                output_tokens = getattr(usage, "candidates_token_count", 0) or 0
                total_tokens = getattr(usage, "total_token_count", input_tokens + output_tokens) or 0

                logger.debug(
                    "Gemini response: tokens=%d latency=%dms attempt=%d",
                    total_tokens, latency_ms, attempt,
                )

                return AIResponse(
                    content=text,
                    provider=self.provider_name,
                    model=self.model_name,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=total_tokens,
                    latency_ms=latency_ms,
                    cost_estimate_usd=self.estimate_cost_usd(input_tokens, output_tokens),
                )

            except Exception as exc:
                last_exc = exc
                logger.warning(
                    "Gemini attempt %d/%d failed: %s",
                    attempt, settings.AI_MAX_RETRIES + 1, exc,
                )
                if attempt <= settings.AI_MAX_RETRIES:
                    import asyncio
                    await asyncio.sleep(attempt * 1.5)  # Exponential backoff

        raise AIProviderError("gemini", str(last_exc)) from last_exc

    async def health_check(self) -> bool:
        try:
            client = self._get_client()
            from google.genai import types
            response = client.models.generate_content(
                model=self.model_name,
                contents="ping",
                config=types.GenerateContentConfig(max_output_tokens=5),
            )
            return bool(response.text)
        except Exception as exc:
            logger.warning("Gemini health check failed: %s", exc)
            return False

    def estimate_cost_usd(self, input_tokens: int, output_tokens: int) -> float:
        return (
            (input_tokens / 1_000_000) * _INPUT_COST_PER_1M
            + (output_tokens / 1_000_000) * _OUTPUT_COST_PER_1M
        )
