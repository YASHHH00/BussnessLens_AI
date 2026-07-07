"""
BusinessLens AI — Retail Domain Plugin: KPI Definitions

Defines the ~10 KPIs computable for the Retail domain.
Each KPI declares its required business fields so the KPI Engine
can skip it gracefully when fields are not mapped.
"""

from __future__ import annotations

from app.plugins.base_plugin import KPIDefinition

RETAIL_KPIS: list[KPIDefinition] = [
    KPIDefinition(
        name="total_revenue",
        display_name="Total Revenue",
        required_fields=("Revenue",),
        formula="SUM(Revenue)",
        aggregation="sum",
        unit="$",
        is_default=True,
        comparison_periods=("mom", "yoy"),
    ),
    KPIDefinition(
        name="total_profit",
        display_name="Total Profit",
        required_fields=("Profit",),
        formula="SUM(Profit)",
        aggregation="sum",
        unit="$",
        is_default=True,
        comparison_periods=("mom", "yoy"),
    ),
    KPIDefinition(
        name="profit_margin",
        display_name="Profit Margin",
        required_fields=("Profit", "Revenue"),
        formula="(SUM(Profit) / SUM(Revenue)) * 100",
        aggregation="ratio",
        unit="%",
        is_default=True,
        comparison_periods=("mom", "yoy"),
    ),
    KPIDefinition(
        name="average_order_value",
        display_name="Average Order Value",
        required_fields=("Revenue", "Order ID"),
        formula="SUM(Revenue) / COUNT(DISTINCT Order ID)",
        aggregation="ratio",
        unit="$",
        is_default=True,
        comparison_periods=("mom",),
    ),
    KPIDefinition(
        name="order_count",
        display_name="Total Orders",
        required_fields=("Order ID",),
        formula="COUNT(DISTINCT Order ID)",
        aggregation="count",
        unit="#",
        is_default=True,
        comparison_periods=("mom", "yoy"),
    ),
    KPIDefinition(
        name="customer_count",
        display_name="Unique Customers",
        required_fields=("Customer",),
        formula="COUNT(DISTINCT Customer)",
        aggregation="count",
        unit="#",
        is_default=True,
        comparison_periods=("mom", "yoy"),
    ),
    KPIDefinition(
        name="total_sales",
        display_name="Total Sales",
        required_fields=("Sales",),
        formula="SUM(Sales)",
        aggregation="sum",
        unit="$",
        is_default=False,
        comparison_periods=("mom", "yoy"),
    ),
    KPIDefinition(
        name="discount_rate",
        display_name="Average Discount Rate",
        required_fields=("Discount",),
        formula="AVG(Discount) * 100",
        aggregation="avg",
        unit="%",
        is_default=False,
        comparison_periods=("mom",),
    ),
    KPIDefinition(
        name="total_quantity",
        display_name="Units Sold",
        required_fields=("Quantity",),
        formula="SUM(Quantity)",
        aggregation="sum",
        unit="#",
        is_default=False,
        comparison_periods=("mom", "yoy"),
    ),
    KPIDefinition(
        name="inventory_total",
        display_name="Total Inventory",
        required_fields=("Inventory",),
        formula="SUM(Inventory)",
        aggregation="sum",
        unit="#",
        is_default=False,
        comparison_periods=(),
    ),
]
