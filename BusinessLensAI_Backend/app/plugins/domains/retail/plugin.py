"""
BusinessLens AI — Retail Domain Plugin

The v1 production domain plugin for Retail & E-Commerce.
Registers all fields, KPIs, templates, rules, and forecast metrics.
"""

from __future__ import annotations

from typing import Any

from app.plugins.base_plugin import (
    BaseDomainPlugin,
    BusinessRule,
    DashboardTemplate,
    KPIDefinition,
)
from app.plugins.domains.retail.fields import RETAIL_FIELDS
from app.plugins.domains.retail.forecasts import RETAIL_FORECASTABLE_METRICS
from app.plugins.domains.retail.kpis import RETAIL_KPIS
from app.plugins.domains.retail.rules import RETAIL_RULES
from app.plugins.domains.retail.templates import RETAIL_TEMPLATES
from app.registry.field_registry import BusinessFieldRegistry


class RetailPlugin(BaseDomainPlugin):
    """
    Retail & E-Commerce domain plugin.

    Covers: brick-and-mortar retail, e-commerce, omnichannel commerce,
    marketplace sellers, and DTC (direct-to-consumer) brands.
    """

    @property
    def name(self) -> str:
        return "retail"

    @property
    def display_name(self) -> str:
        return "Retail & E-Commerce"

    @property
    def version(self) -> str:
        return "1.0.0"

    def register_fields(self, registry: BusinessFieldRegistry) -> None:
        """Register all 22 retail business fields into the registry."""
        registry.register_many(RETAIL_FIELDS)

    def get_kpi_definitions(self) -> list[KPIDefinition]:
        return RETAIL_KPIS

    def get_dashboard_templates(self) -> list[DashboardTemplate]:
        return RETAIL_TEMPLATES

    def get_business_rules(self) -> list[BusinessRule]:
        return RETAIL_RULES

    def get_forecastable_metrics(self) -> list[str]:
        return RETAIL_FORECASTABLE_METRICS

    def get_ai_prompt_context(self) -> dict[str, Any]:
        """
        Domain context injected into every AI prompt.
        Helps the AI understand the business context during schema analysis.
        """
        return {
            "domain": "Retail & E-Commerce",
            "typical_tables": [
                "orders", "order_items", "products", "customers",
                "inventory", "suppliers", "categories", "shipments",
            ],
            "typical_relationships": [
                "orders → order_items (one-to-many)",
                "order_items → products (many-to-one)",
                "orders → customers (many-to-one)",
                "products → categories (many-to-one)",
                "order_items → inventory (many-to-one)",
            ],
            "business_context": (
                "This is a retail/e-commerce database. "
                "Look for sales transactions, product catalogs, customer records, "
                "inventory levels, and shipping information."
            ),
        }
