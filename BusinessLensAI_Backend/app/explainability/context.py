"""
BusinessLens AI — Explainability Framework: Context Dataclass

ExplanationContext is the single structured output of every explainer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class ExplanationContext:
    """
    Unified explanation context for any platform artifact.

    Every engine that produces a computable result (KPI, Widget, Dashboard,
    Insight, Forecast, Rule, Recommendation, Mapping) populates and returns
    an ExplanationContext so the user can understand exactly how it was derived.
    """

    artifact_type: str
    """Type of artifact being explained: 'kpi', 'widget', 'dashboard', 'insight',
    'forecast', 'rule', 'recommendation', 'mapping'"""

    artifact_id: str
    """Unique identifier for the artifact (e.g. KPI name, dashboard ID)."""

    title: str
    """Human-readable title for the explanation UI."""

    source_tables: list[str] = field(default_factory=list)
    """Physical database tables this result was derived from."""

    source_columns: list[str] = field(default_factory=list)
    """Physical columns used in the computation."""

    business_fields: list[str] = field(default_factory=list)
    """Business field names (from registry) this result maps to."""

    aggregations: list[str] = field(default_factory=list)
    """SQL aggregations applied: ['SUM(revenue)', 'COUNT(DISTINCT customer_id)']"""

    filters_applied: list[dict] = field(default_factory=list)
    """Filters applied: [{'field': 'Order Date', 'op': '>=', 'value': '2024-01-01'}]"""

    formula: str | None = None
    """Human-readable formula: 'SUM(Profit) / SUM(Revenue) * 100'"""

    related_kpis: list[str] = field(default_factory=list)
    """KPI names that contributed to this result."""

    generated_sql: str | None = None
    """The actual SQL executed (role-gated — Data Analyst + Admin only)."""

    rule_evaluation: str | None = None
    """For rules engine results: the rule logic that triggered."""

    ai_reasoning_summary: str | None = None
    """For AI-assisted results: short summary of AI reasoning (not raw prompt)."""

    join_paths: list[str] = field(default_factory=list)
    """Table join paths: ['orders → order_items ON order_items.order_id = orders.id']"""

    date_range: str | None = None
    """Date range applied: '2024-01-01 to 2024-12-31'"""

    data_source: str = "database"
    """Where data came from: 'database', 'file_upload', 'cache'"""

    computed_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    """When this explanation was generated."""

    confidence: float | None = None
    """Optional confidence score (0.0 - 1.0) for AI-assisted results."""

    def to_dict(self) -> dict:
        return {
            "artifact_type": self.artifact_type,
            "artifact_id": self.artifact_id,
            "title": self.title,
            "source_tables": self.source_tables,
            "source_columns": self.source_columns,
            "business_fields": self.business_fields,
            "aggregations": self.aggregations,
            "filters_applied": self.filters_applied,
            "formula": self.formula,
            "related_kpis": self.related_kpis,
            "generated_sql": self.generated_sql,
            "rule_evaluation": self.rule_evaluation,
            "ai_reasoning_summary": self.ai_reasoning_summary,
            "join_paths": self.join_paths,
            "date_range": self.date_range,
            "data_source": self.data_source,
            "computed_at": self.computed_at.isoformat(),
            "confidence": self.confidence,
        }
