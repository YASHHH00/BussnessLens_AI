"""
BusinessLens AI — AI Provider Abstract Base Class

All AI provider implementations (Gemini, OpenAI) implement this interface.
The rest of the platform never imports a provider directly — only BaseAIProvider.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class AIRequest:
    """Standardized AI request envelope."""
    prompt: str
    system_instruction: str | None = None
    temperature: float = 0.2          # Low temperature for deterministic analysis
    max_output_tokens: int = 8192
    response_format: str = "json"     # "json" | "text"
    metadata: dict[str, Any] | None = None


@dataclass
class AIResponse:
    """Standardized AI response envelope."""
    content: str                      # Raw text / JSON string from the model
    provider: str                     # "gemini" | "openai"
    model: str                        # e.g. "gemini-2.0-flash", "gpt-4o-mini"
    input_tokens: int
    output_tokens: int
    total_tokens: int
    latency_ms: int
    cost_estimate_usd: float | None = None  # Optional — for audit/cost tracking

    def parse_json(self) -> dict[str, Any]:
        """Parse the content as JSON, stripping markdown code fences if present."""
        import json
        content = self.content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            # Strip opening ``` and closing ```
            content = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        return json.loads(content)


class BaseAIProvider(ABC):
    """
    Abstract AI provider interface.

    Responsibilities:
    - Execute prompts with structured input/output
    - Track token usage for cost optimization
    - Handle retries on transient errors
    - Never generate SQL (enforced by prompt templates)
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Unique provider identifier: 'gemini' | 'openai'"""
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        """The specific model being used."""
        ...

    @abstractmethod
    async def complete(self, request: AIRequest) -> AIResponse:
        """
        Send a prompt and return a structured response.
        Handles retries internally up to AI_MAX_RETRIES times.
        Raises AIProviderError on unrecoverable failure.
        """
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if the provider is reachable with current credentials."""
        ...

    def estimate_cost_usd(self, input_tokens: int, output_tokens: int) -> float:
        """
        Optional: estimate USD cost for a request.
        Override in concrete providers for accurate pricing.
        """
        return 0.0
