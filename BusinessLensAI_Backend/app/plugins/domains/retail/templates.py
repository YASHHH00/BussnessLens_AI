"""
BusinessLens AI — Retail Domain Plugin: Dashboard Templates

Defines 5 dashboard templates for the Retail domain.
Used by the Dashboard Recommender and Dashboard Generator.
"""

from __future__ import annotations

from app.plugins.base_plugin import DashboardTemplate, WidgetTemplate

RETAIL_TEMPLATES: list[DashboardTemplate] = [

    DashboardTemplate(
        name="executive",
        display_name="Executive Dashboard",
        description="High-level KPI overview for executive stakeholders.",
        required_fields=("Revenue", "Profit", "Order ID", "Order Date"),
        is_default=True,
        widgets=(
            WidgetTemplate(
                title="Total Revenue", widget_type="kpi_card",
                kpi_name="total_revenue", metric=None, aggregation="sum",
                group_by=None, position={"row": 0, "col": 0, "width": 3, "height": 1},
            ),
            WidgetTemplate(
                title="Total Profit", widget_type="kpi_card",
                kpi_name="total_profit", metric=None, aggregation="sum",
                group_by=None, position={"row": 0, "col": 3, "width": 3, "height": 1},
            ),
            WidgetTemplate(
                title="Profit Margin", widget_type="kpi_card",
                kpi_name="profit_margin", metric=None, aggregation="ratio",
                group_by=None, position={"row": 0, "col": 6, "width": 3, "height": 1},
            ),
            WidgetTemplate(
                title="Total Orders", widget_type="kpi_card",
                kpi_name="order_count", metric=None, aggregation="count",
                group_by=None, position={"row": 0, "col": 9, "width": 3, "height": 1},
            ),
            WidgetTemplate(
                title="Revenue Trend", widget_type="line_chart",
                kpi_name=None, metric="Revenue", aggregation="sum",
                group_by="Order Date", position={"row": 1, "col": 0, "width": 8, "height": 3},
            ),
            WidgetTemplate(
                title="Revenue by Region", widget_type="bar_chart",
                kpi_name=None, metric="Revenue", aggregation="sum",
                group_by="Region", position={"row": 1, "col": 8, "width": 4, "height": 3},
            ),
        ),
    ),

    DashboardTemplate(
        name="sales",
        display_name="Sales Dashboard",
        description="Detailed sales performance analysis.",
        required_fields=("Sales", "Order Date", "Category"),
        is_default=True,
        widgets=(
            WidgetTemplate(
                title="Total Sales", widget_type="kpi_card",
                kpi_name="total_sales", metric=None, aggregation="sum",
                group_by=None, position={"row": 0, "col": 0, "width": 3, "height": 1},
            ),
            WidgetTemplate(
                title="Average Order Value", widget_type="kpi_card",
                kpi_name="average_order_value", metric=None, aggregation="ratio",
                group_by=None, position={"row": 0, "col": 3, "width": 3, "height": 1},
            ),
            WidgetTemplate(
                title="Units Sold", widget_type="kpi_card",
                kpi_name="total_quantity", metric=None, aggregation="sum",
                group_by=None, position={"row": 0, "col": 6, "width": 3, "height": 1},
            ),
            WidgetTemplate(
                title="Sales by Category", widget_type="bar_chart",
                kpi_name=None, metric="Sales", aggregation="sum",
                group_by="Category", position={"row": 1, "col": 0, "width": 6, "height": 3},
            ),
            WidgetTemplate(
                title="Sales Over Time", widget_type="line_chart",
                kpi_name=None, metric="Sales", aggregation="sum",
                group_by="Order Date", position={"row": 1, "col": 6, "width": 6, "height": 3},
            ),
        ),
    ),

    DashboardTemplate(
        name="customer",
        display_name="Customer Dashboard",
        description="Customer acquisition and retention metrics.",
        required_fields=("Customer", "Revenue", "Order Date"),
        is_default=False,
        widgets=(
            WidgetTemplate(
                title="Unique Customers", widget_type="kpi_card",
                kpi_name="customer_count", metric=None, aggregation="count",
                group_by=None, position={"row": 0, "col": 0, "width": 4, "height": 1},
            ),
            WidgetTemplate(
                title="Revenue per Customer", widget_type="kpi_card",
                kpi_name=None, metric="Revenue", aggregation="avg",
                group_by=None, position={"row": 0, "col": 4, "width": 4, "height": 1},
            ),
            WidgetTemplate(
                title="New Customers Over Time", widget_type="line_chart",
                kpi_name=None, metric="Customer", aggregation="count",
                group_by="Order Date", position={"row": 1, "col": 0, "width": 12, "height": 3},
            ),
        ),
    ),

    DashboardTemplate(
        name="inventory",
        display_name="Inventory Dashboard",
        description="Stock levels and inventory management overview.",
        required_fields=("Inventory", "Product"),
        is_default=False,
        widgets=(
            WidgetTemplate(
                title="Total Inventory", widget_type="kpi_card",
                kpi_name="inventory_total", metric=None, aggregation="sum",
                group_by=None, position={"row": 0, "col": 0, "width": 4, "height": 1},
            ),
            WidgetTemplate(
                title="Inventory by Product", widget_type="bar_chart",
                kpi_name=None, metric="Inventory", aggregation="sum",
                group_by="Product", position={"row": 1, "col": 0, "width": 12, "height": 3},
            ),
        ),
    ),

    DashboardTemplate(
        name="forecast",
        display_name="Forecast Dashboard",
        description="Revenue and sales forecasting for the upcoming period.",
        required_fields=("Revenue", "Order Date"),
        is_default=False,
        widgets=(
            WidgetTemplate(
                title="Revenue Forecast", widget_type="line_chart",
                kpi_name=None, metric="Revenue", aggregation="sum",
                group_by="Order Date", position={"row": 0, "col": 0, "width": 12, "height": 4},
            ),
        ),
    ),
]
