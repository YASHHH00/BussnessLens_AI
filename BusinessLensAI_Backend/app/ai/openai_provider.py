"""
BusinessLens AI — OpenAI Provider (gpt-4o-mini, secondary provider)

Secondary provider — used when AI_PROVIDER=openai or as fallback.
Implements same BaseAIProvider interface as GeminiProvider.
"""

from __future__ import annotations

import time

from app.ai.base_provider import AIRequest, AIResponse, BaseAIProvider
from app.core.config import settings
from app.core.exceptions import AIProviderError
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# gpt-4o-mini pricing (per 1M tokens)
_INPUT_COST_PER_1M = 0.15
_OUTPUT_COST_PER_1M = 0.60


class OpenAIProvider(BaseAIProvider):
    """
    OpenAI provider using gpt-4o-mini.
    Acts as secondary provider or can be configured as primary.
    """

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(api_key=self._api_key)
            except Exception as exc:
                raise AIProviderError("openai", f"Failed to init client: {exc}") from exc
        return self._client

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return "gpt-4o-mini"

    async def complete(self, request: AIRequest) -> AIResponse:
        client = self._get_client()
        last_exc: Exception | None = None

        messages = []
        if request.system_instruction:
            messages.append({"role": "system", "content": request.system_instruction})
        messages.append({"role": "user", "content": request.prompt})

        for attempt in range(1, settings.AI_MAX_RETRIES + 2):
            try:
                t0 = time.monotonic()

                kwargs: dict = dict(
                    model=self.model_name,
                    messages=messages,
                    temperature=request.temperature,
                    max_tokens=request.max_output_tokens,
                )
                if request.response_format == "json":
                    kwargs["response_format"] = {"type": "json_object"}

                response = await client.chat.completions.create(**kwargs)
                latency_ms = int((time.monotonic() - t0) * 1000)

                content = response.choices[0].message.content or ""
                usage = response.usage
                input_tokens = usage.prompt_tokens if usage else 0
                output_tokens = usage.completion_tokens if usage else 0
                total_tokens = usage.total_tokens if usage else 0

                return AIResponse(
                    content=content,
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
                logger.warning("OpenAI attempt %d failed: %s", attempt, exc)
                if attempt <= settings.AI_MAX_RETRIES:
                    import asyncio
                    await asyncio.sleep(attempt * 1.5)

        raise AIProviderError("openai", str(last_exc)) from last_exc

    async def health_check(self) -> bool:
        try:
            client = self._get_client()
            response = await client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=5,
            )
            return bool(response.choices)
        except Exception as exc:
            logger.warning("OpenAI health check failed: %s", exc)
            return False

    def estimate_cost_usd(self, input_tokens: int, output_tokens: int) -> float:
        return (
            (input_tokens / 1_000_000) * _INPUT_COST_PER_1M
            + (output_tokens / 1_000_000) * _OUTPUT_COST_PER_1M
        )
