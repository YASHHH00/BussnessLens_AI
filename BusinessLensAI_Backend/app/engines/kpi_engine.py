"""
BusinessLens AI — KPI & Rules Engine

Evaluates domain KPIs and deterministic business rules over a connection's SemanticContext.
Uses AnalyticsEngine for query execution so all joins and identifier rules are respected.
"""

from __future__ import annotations

from typing import Any

from app.connectors.base_connector import BaseDBConnector
from app.core.logging_config import get_logger
from app.engines.analytics_engine import AnalyticsEngine
from app.plugins.base_plugin import BusinessRule, KPIDefinition
from app.registry.field_registry import BusinessFieldRegistry
from app.schemas.analytics import AnalyticsQueryRequest, KPIEvaluationResult, RuleTriggerAlert
from app.semantic.semantic_context import SemanticContext

logger = get_logger(__name__)


class KPIEngine:
    """
    Evaluates domain KPIs and business rules.
    Skips KPIs/rules gracefully if required business fields are not mapped in SemanticContext.
    """

    def __init__(self, registry: BusinessFieldRegistry, analytics_engine: AnalyticsEngine) -> None:
        self._registry = registry
        self._analytics = analytics_engine

    async def evaluate_all_kpis(
        self,
        connector: BaseDBConnector,
        context: SemanticContext,
        kpis: list[KPIDefinition],
    ) -> list[KPIEvaluationResult]:
        """
        Evaluate a list of domain KPIs.
        If a KPI's required fields are not present in SemanticContext, skips or returns None value.
        """
        results: list[KPIEvaluationResult] = []

        for kpi in kpis:
            # Check field readiness
            missing_fields = [f for f in kpi.required_fields if not context.has_field(f)]
            if missing_fields:
                logger.debug("Skipping KPI %s — missing fields: %s", kpi.name, missing_fields)
                continue

            try:
                # We can evaluate single metric KPIs or ratio KPIs
                val = await self._compute_kpi_value(connector, context, kpi)
                formatted = self._format_value(val, kpi.unit)
                results.append(
                    KPIEvaluationResult(
                        kpi_name=kpi.name,
                        display_name=kpi.display_name,
                        category="metric",
                        current_value=val,
                        formatted_value=formatted,
                        unit=kpi.unit,
                    )
                )
            except Exception as exc:
                logger.warning("Error evaluating KPI %s: %s", kpi.name, exc)

        return results

    async def _compute_kpi_value(
        self,
        connector: BaseDBConnector,
        context: SemanticContext,
        kpi: KPIDefinition,
    ) -> float | None:
        if kpi.aggregation == "ratio" and len(kpi.required_fields) >= 2:
            num_field = kpi.required_fields[0]
            den_field = kpi.required_fields[1]
            req = AnalyticsQueryRequest(metrics=[num_field, den_field], limit=1)
            res = await self._analytics.execute_query(connector, context, req)
            if not res.rows:
                return None
            row = res.rows[0]
            num_val = float(row.get(num_field) or 0.0)
            den_val = float(row.get(den_field) or 0.0)
            if den_val == 0:
                return 0.0
            ratio = (num_val / den_val)
            if kpi.unit == "%":
                ratio *= 100.0
            return ratio

        # Single field aggregation
        metric_field = kpi.required_fields[0]
        req = AnalyticsQueryRequest(metrics=[metric_field], limit=1)
        res = await self._analytics.execute_query(connector, context, req)
        if not res.rows:
            return None
        return float(res.rows[0].get(metric_field) or 0.0)

    def _format_value(self, val: float | None, unit: str) -> str:
        if val is None:
            return "N/A"
        if unit == "$":
            return f"${val:,.2f}"
        if unit == "%":
            return f"{val:.1f}%"
        return f"{val:,.0f}"

    async def evaluate_rules(
        self,
        connector: BaseDBConnector,
        context: SemanticContext,
        rules: list[BusinessRule],
        kpi_results: list[KPIEvaluationResult],
    ) -> list[RuleTriggerAlert]:
        """
        Evaluate deterministic business rules over KPI results or quick queries.
        Produces RuleTriggerAlert items if conditions trigger.
        """
        alerts: list[RuleTriggerAlert] = []
        kpi_map = {k.display_name: k.current_value for k in kpi_results}
        kpi_map.update({k.kpi_name: k.current_value for k in kpi_results})

        for rule in rules:
            missing_fields = [f for f in rule.required_fields if not context.has_field(f)]
            if missing_fields:
                continue

            try:
                # Check threshold rule against KPI map or direct query
                val: float | None = None
                target_field = rule.required_fields[0]
                if target_field in kpi_map:
                    val = kpi_map[target_field]
                else:
                    req = AnalyticsQueryRequest(metrics=[target_field], limit=1)
                    res = await self._analytics.execute_query(connector, context, req)
                    if res.rows:
                        val = float(res.rows[0].get(target_field) or 0.0)

                if val is None:
                    continue

                triggered = False
                op = rule.comparison_operator
                th = rule.threshold
                if op == "lt" and val < th:
                    triggered = True
                elif op == "gt" and val > th:
                    triggered = True
                elif op == "eq" and val == th:
                    triggered = True

                if triggered:
                    msg = rule.description_template.format(value=val)
                    alerts.append(
                        RuleTriggerAlert(
                            rule_name=rule.name,
                            description=rule.display_name,
                            severity=rule.severity,
                            metric=target_field,
                            threshold_value=th,
                            actual_value=val,
                            message=msg,
                        )
                    )
            except Exception as exc:
                logger.warning("Error evaluating rule %s: %s", rule.name, exc)

        return alerts
