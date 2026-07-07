"""
BusinessLens AI — Explainability Framework: Base Explainer

All 8 artifact-specific explainers implement this interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.explainability.context import ExplanationContext


class BaseExplainer(ABC):
    """
    Abstract base for all explainers.

    Explainers are stateless — they receive the artifact + its generation metadata
    and return an ExplanationContext. They are not persisted themselves.
    """

    @property
    @abstractmethod
    def artifact_type(self) -> str:
        """Unique string identifier for the artifact type this explainer handles."""
        ...

    @abstractmethod
    async def explain(self, artifact_id: str, **kwargs: Any) -> ExplanationContext:
        """
        Generate an ExplanationContext for the given artifact.

        kwargs contain artifact-specific data:
        - For KPI: kpi_definition, semantic_context, generated_sql, filters
        - For Widget: widget_def, semantic_context, generated_sql
        - For Forecast: forecast_result, model_info
        etc.
        """
        ...


class KPIExplainer(BaseExplainer):
    """Explains how a KPI result was computed."""

    artifact_type = "kpi"

    async def explain(self, artifact_id: str, **kwargs: Any) -> ExplanationContext:
        kpi_def = kwargs.get("kpi_definition")
        semantic_ctx = kwargs.get("semantic_context")
        generated_sql = kwargs.get("generated_sql")
        filters = kwargs.get("filters", [])

        return ExplanationContext(
            artifact_type=self.artifact_type,
            artifact_id=artifact_id,
            title=f"How '{kpi_def.display_name if kpi_def else artifact_id}' was computed",
            business_fields=list(kpi_def.required_fields) if kpi_def else [],
            formula=kpi_def.formula if kpi_def else None,
            aggregations=[kpi_def.aggregation] if kpi_def else [],
            filters_applied=filters,
            generated_sql=generated_sql,
            related_kpis=[artifact_id],
            source_tables=kwargs.get("source_tables", []),
            source_columns=kwargs.get("source_columns", []),
            date_range=kwargs.get("date_range"),
        )


class MappingExplainer(BaseExplainer):
    """Explains how AI mapped a database column to a business field."""

    artifact_type = "mapping"

    async def explain(self, artifact_id: str, **kwargs: Any) -> ExplanationContext:
        mapping = kwargs.get("mapping")
        return ExplanationContext(
            artifact_type=self.artifact_type,
            artifact_id=artifact_id,
            title=f"Why column '{artifact_id}' was mapped to this business field",
            source_columns=[artifact_id],
            business_fields=[kwargs.get("business_field", "")],
            ai_reasoning_summary=kwargs.get("ai_reasoning"),
            confidence=kwargs.get("confidence"),
            data_source="ai_analysis",
        )


class ForecastExplainer(BaseExplainer):
    """Explains how a forecast was generated."""

    artifact_type = "forecast"

    async def explain(self, artifact_id: str, **kwargs: Any) -> ExplanationContext:
        return ExplanationContext(
            artifact_type=self.artifact_type,
            artifact_id=artifact_id,
            title=f"How the forecast for '{artifact_id}' was generated",
            business_fields=[kwargs.get("metric", "")],
            formula=kwargs.get("model_formula"),
            ai_reasoning_summary=kwargs.get("model_description"),
            date_range=kwargs.get("forecast_horizon"),
            data_source=kwargs.get("data_source", "database"),
            confidence=kwargs.get("model_accuracy"),
        )


class RuleExplainer(BaseExplainer):
    """Explains why a business rule was triggered."""

    artifact_type = "rule"

    async def explain(self, artifact_id: str, **kwargs: Any) -> ExplanationContext:
        rule = kwargs.get("rule")
        return ExplanationContext(
            artifact_type=self.artifact_type,
            artifact_id=artifact_id,
            title=f"Why alert '{rule.display_name if rule else artifact_id}' was triggered",
            business_fields=list(rule.required_fields) if rule else [],
            rule_evaluation=kwargs.get("rule_logic"),
            formula=kwargs.get("evaluation_details"),
            data_source="rules_engine",
        )
