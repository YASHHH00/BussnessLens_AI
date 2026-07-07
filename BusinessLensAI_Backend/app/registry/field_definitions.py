"""
BusinessLens AI — FieldDefinition Dataclass

Describes a single business field recognized by the platform.
All metadata for validation, AI prompting, semantic resolution,
and display is centralized here.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.registry.field_types import FieldCategory


@dataclass(frozen=True)
class FieldDefinition:
    """
    Complete description of a business field.

    Instances are registered by domain plugins at startup and consumed
    by every subsystem: mapping validation, analytics engine, KPI engine,
    rules engine, AI prompts, semantic layer, and forecast service.

    Adding a new domain is as simple as registering FieldDefinitions
    for its vocabulary — no engine code changes required.
    """

    name: str
    """Canonical name used everywhere in the platform. e.g. 'Revenue', 'Order Date'"""

    category: FieldCategory
    """What role this field plays (METRIC / DIMENSION / TEMPORAL / IDENTIFIER)."""

    expected_types: tuple[str, ...]
    """
    Physical column types this field should map to.
    e.g. ('numeric', 'decimal', 'float', 'integer', 'double', 'real')
    Used by mapping validation Rule #1/#2.
    """

    aliases: tuple[str, ...]
    """
    Common column name aliases for AI fuzzy matching.
    e.g. ('total_sales', 'net_sales', 'sales_amount', 'revenue')
    """

    description: str
    """Human-readable description shown in the mapping review UI."""

    is_forecastable: bool
    """Whether this field can be used as a forecast target metric."""

    conflicting_categories: tuple[FieldCategory, ...] = field(default_factory=tuple)
    """
    Categories this field must NOT map to.
    e.g. Revenue cannot map to TEMPORAL (mapping Rule #6).
    """

    default_aggregation: str = "sum"
    """
    Default SQL aggregation for this field in analytics queries.
    e.g. 'sum', 'avg', 'count', 'min', 'max'
    Consumed by the Semantic Layer.
    """

    display_format: str | None = None
    """
    Optional frontend display format string.
    e.g. '$#,##0.00' for currency, '0.0%' for percentage, '#,##0' for count.
    Consumed by the Semantic Layer and dashboard rendering.
    """

    display_name: str | None = None
    """
    Human-readable display name if different from `name`.
    Falls back to `name` if None.
    """

    @property
    def resolved_display_name(self) -> str:
        return self.display_name or self.name

    def is_metric(self) -> bool:
        return self.category == FieldCategory.METRIC

    def is_dimension(self) -> bool:
        return self.category == FieldCategory.DIMENSION

    def is_temporal(self) -> bool:
        return self.category == FieldCategory.TEMPORAL

    def is_identifier(self) -> bool:
        return self.category == FieldCategory.IDENTIFIER

    def __str__(self) -> str:
        return f"FieldDefinition({self.name}, {self.category})"
