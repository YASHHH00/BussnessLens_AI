"""
BusinessLens AI — Domain Plugin Abstract Base Class

Every domain vertical (Retail, Food Delivery, Warehouse, Healthcare, etc.)
implements this interface. The core platform NEVER imports domain-specific
logic directly — it always goes through the PluginManager.

This makes BusinessLens AI core completely domain-agnostic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from app.registry.field_definitions import FieldDefinition
from app.registry.field_registry import BusinessFieldRegistry
from app.registry.field_types import FieldCategory


# ------------------------------------------------------------------ #
# Plugin-provided data structures
# ------------------------------------------------------------------ #

@dataclass(frozen=True)
class KPIDefinition:
    """A computable KPI registered by a domain plugin."""
    name: str
    display_name: str
    required_fields: tuple[str, ...]        # Business field names needed
    formula: str                            # Human-readable: "SUM(Sales) / COUNT(Orders)"
    aggregation: str                        # "sum", "avg", "count", "ratio", "custom"
    unit: str                               # "$", "%", "#", "days"
    is_default: bool = False                # Show on Executive dashboard by default?
    comparison_periods: tuple[str, ...] = ("mom", "yoy")  # Period-over-period comparison


@dataclass(frozen=True)
class WidgetTemplate:
    """Template for a single widget within a dashboard template."""
    title: str
    widget_type: str        # "kpi_card", "line_chart", "bar_chart", "pie_chart", "table"
    kpi_name: str | None    # Reference to KPIDefinition.name (for KPI cards)
    metric: str | None      # Business field name (for charts)
    aggregation: str
    group_by: str | None    # Business field name for grouping
    default_filters: dict[str, Any] = field(default_factory=dict)
    position: dict[str, int] = field(default_factory=dict)  # {row, col, width, height}


@dataclass(frozen=True)
class DashboardTemplate:
    """A pre-defined dashboard layout registered by a domain plugin."""
    name: str
    display_name: str
    description: str
    required_fields: tuple[str, ...]    # Min fields needed to enable this dashboard
    widgets: tuple[WidgetTemplate, ...]
    is_default: bool = False            # Auto-generate when mappings are saved?


@dataclass(frozen=True)
class BusinessRule:
    """A deterministic business rule for the Rules Engine."""
    name: str
    display_name: str
    severity: str                       # "critical", "warning", "info"
    required_fields: tuple[str, ...]    # Business fields needed to evaluate
    condition_type: str                 # "threshold", "comparison", "anomaly", "missing"
    threshold: float | None = None
    comparison_operator: str = "lt"     # "lt", "gt", "drop_pct", "spike_pct"
    comparison_period: str | None = None  # "mom", "wow", "yoy"
    description_template: str = ""      # "{field} value: {value}"


# ------------------------------------------------------------------ #
# Abstract Base Plugin
# ------------------------------------------------------------------ #

class BaseDomainPlugin(ABC):
    """
    Contract every domain plugin must fulfill.

    Lifecycle:
    1. PluginManager discovers and instantiates the plugin.
    2. PluginManager calls `register_fields(registry)` → populates BusinessFieldRegistry.
    3. All engines access fields through the registry.
    4. Engines call get_kpi_definitions() / get_dashboard_templates() / etc.
       to get domain-specific definitions without importing the plugin directly.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique plugin identifier. e.g. 'retail'"""
        ...

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable plugin name. e.g. 'Retail & E-Commerce'"""
        ...

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version string. e.g. '1.0.0'"""
        ...

    @abstractmethod
    def register_fields(self, registry: BusinessFieldRegistry) -> None:
        """Register all business field definitions for this domain into the registry."""
        ...

    @abstractmethod
    def get_kpi_definitions(self) -> list[KPIDefinition]:
        """Return all KPIs computable in this domain."""
        ...

    @abstractmethod
    def get_dashboard_templates(self) -> list[DashboardTemplate]:
        """Return all dashboard templates for this domain."""
        ...

    @abstractmethod
    def get_business_rules(self) -> list[BusinessRule]:
        """Return all deterministic business rules for insight detection."""
        ...

    @abstractmethod
    def get_forecastable_metrics(self) -> list[str]:
        """Return business field names eligible for forecasting."""
        ...

    @abstractmethod
    def get_ai_prompt_context(self) -> dict[str, Any]:
        """
        Return domain-specific context injected into AI prompts.
        Helps AI understand the domain vocabulary during schema analysis.
        """
        ...

    def __repr__(self) -> str:
        return f"<DomainPlugin name={self.name} version={self.version}>"
