"""
BusinessLens AI — Retail Domain Plugin: Business Rules

Defines deterministic business rules evaluated by the Rules Engine
BEFORE AI is involved in insight generation.

Rules are pure data — no SQL, no computation logic.
The Rules Engine interprets them against the Analytics Engine output.
"""

from __future__ import annotations

from app.plugins.base_plugin import BusinessRule

RETAIL_RULES: list[BusinessRule] = [
    BusinessRule(
        name="negative_profit",
        display_name="Negative Profit Detected",
        severity="critical",
        required_fields=("Profit",),
        condition_type="threshold",
        threshold=0.0,
        comparison_operator="lt",
        description_template="Total profit is negative: {value}. Immediate review recommended.",
    ),
    BusinessRule(
        name="revenue_drop_mom",
        display_name="Revenue Drop Month-over-Month",
        severity="critical",
        required_fields=("Revenue", "Order Date"),
        condition_type="comparison",
        threshold=-10.0,      # -10% threshold
        comparison_operator="drop_pct",
        comparison_period="mom",
        description_template="Revenue dropped {value:.1f}% month-over-month.",
    ),
    BusinessRule(
        name="revenue_drop_yoy",
        display_name="Revenue Drop Year-over-Year",
        severity="warning",
        required_fields=("Revenue", "Order Date"),
        condition_type="comparison",
        threshold=-15.0,
        comparison_operator="drop_pct",
        comparison_period="yoy",
        description_template="Revenue dropped {value:.1f}% year-over-year.",
    ),
    BusinessRule(
        name="sales_spike",
        display_name="Unusual Sales Spike",
        severity="info",
        required_fields=("Sales", "Order Date"),
        condition_type="comparison",
        threshold=50.0,       # +50% spike threshold
        comparison_operator="spike_pct",
        comparison_period="wow",
        description_template="Sales spiked {value:.1f}% week-over-week — verify data integrity.",
    ),
    BusinessRule(
        name="high_discount_rate",
        display_name="Abnormally High Discounts",
        severity="warning",
        required_fields=("Discount",),
        condition_type="threshold",
        threshold=0.30,       # 30% average discount
        comparison_operator="gt",
        description_template="Average discount rate is {value:.1%} — exceeds the 30% threshold.",
    ),
    BusinessRule(
        name="low_inventory",
        display_name="Low Inventory Alert",
        severity="warning",
        required_fields=("Inventory",),
        condition_type="threshold",
        threshold=10.0,       # Fewer than 10 units
        comparison_operator="lt",
        description_template="Inventory is critically low: {value} units remaining.",
    ),
    BusinessRule(
        name="low_profit_margin",
        display_name="Low Profit Margin",
        severity="warning",
        required_fields=("Profit", "Revenue"),
        condition_type="threshold",
        threshold=5.0,        # < 5% profit margin
        comparison_operator="lt",
        description_template="Profit margin is {value:.1f}% — below the 5% minimum threshold.",
    ),
    BusinessRule(
        name="zero_orders",
        display_name="No Orders in Period",
        severity="critical",
        required_fields=("Order ID", "Order Date"),
        condition_type="threshold",
        threshold=0.0,
        comparison_operator="lt",
        description_template="No orders recorded in the selected period.",
    ),
]
