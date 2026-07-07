"""
BusinessLens AI — Explainability Service

Routes explain requests to the correct explainer by artifact type.
Called from the /explain endpoint.
"""

from __future__ import annotations

from typing import Any

from app.core.exceptions import NotFoundError
from app.explainability.base_explainer import (
    BaseExplainer, KPIExplainer, MappingExplainer, ForecastExplainer, RuleExplainer,
)
from app.explainability.context import ExplanationContext


class ExplainabilityService:
    """
    Routes explain requests to the correct explainer by artifact type.

    Explainers are registered at initialization — adding a new explainer
    is a one-line addition to the registry, not a modification of the service.
    """

    def __init__(self) -> None:
        self._explainers: dict[str, BaseExplainer] = {}
        # Register all built-in explainers
        for explainer in [KPIExplainer(), MappingExplainer(), ForecastExplainer(), RuleExplainer()]:
            self._explainers[explainer.artifact_type] = explainer

    def register(self, explainer: BaseExplainer) -> None:
        """Register a custom explainer (used by plugins for domain-specific artifacts)."""
        self._explainers[explainer.artifact_type] = explainer

    async def explain(
        self,
        artifact_type: str,
        artifact_id: str,
        role: str,
        **kwargs: Any,
    ) -> ExplanationContext:
        """
        Dispatch to the appropriate explainer.
        Role-gates the `generated_sql` field — Data Analyst + Admin only.
        """
        explainer = self._explainers.get(artifact_type)
        if explainer is None:
            valid = ", ".join(self._explainers.keys())
            raise NotFoundError(
                f"No explainer registered for artifact type '{artifact_type}'. "
                f"Available types: {valid}"
            )

        context = await explainer.explain(artifact_id, **kwargs)

        # Role-gate SQL visibility
        if role not in ("data_analyst", "admin"):
            context.generated_sql = None

        return context

    def list_supported_types(self) -> list[str]:
        return list(self._explainers.keys())
