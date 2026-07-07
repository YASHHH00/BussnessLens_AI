"""Warehouse Plugin — Stub for v2."""
from app.plugins.base_plugin import BaseDomainPlugin, KPIDefinition, DashboardTemplate, BusinessRule
from app.registry.field_registry import BusinessFieldRegistry
from typing import Any

class WarehousePlugin(BaseDomainPlugin):
    @property
    def name(self) -> str: return "warehouse"
    @property
    def display_name(self) -> str: return "Warehouse Management"
    @property
    def version(self) -> str: return "0.0.0-stub"
    def register_fields(self, registry: BusinessFieldRegistry) -> None:
        raise NotImplementedError("Warehouse plugin is planned for v2.")
    def get_kpi_definitions(self) -> list[KPIDefinition]: raise NotImplementedError
    def get_dashboard_templates(self) -> list[DashboardTemplate]: raise NotImplementedError
    def get_business_rules(self) -> list[BusinessRule]: raise NotImplementedError
    def get_forecastable_metrics(self) -> list[str]: raise NotImplementedError
    def get_ai_prompt_context(self) -> dict[str, Any]: raise NotImplementedError
