"""
BusinessLens AI — Retail Domain Plugin: Field Definitions

Registers ~15 business fields for the Retail & E-Commerce domain.
All field metadata (types, aliases, aggregations, formats) is defined here.
"""

from __future__ import annotations

from app.registry.field_definitions import FieldDefinition
from app.registry.field_types import FieldCategory

# Convenience shorthand
M = FieldCategory.METRIC
D = FieldCategory.DIMENSION
T = FieldCategory.TEMPORAL
I = FieldCategory.IDENTIFIER


RETAIL_FIELDS: list[FieldDefinition] = [

    # ------------------------------------------------------------------ #
    # METRICS
    # ------------------------------------------------------------------ #
    FieldDefinition(
        name="Sales",
        category=M,
        expected_types=("numeric", "decimal", "float", "double", "real", "integer", "bigint", "money"),
        aliases=("total_sales", "net_sales", "sales_amount", "sale_value", "gross_sales"),
        description="Total sales amount (before or after discounts depending on schema).",
        is_forecastable=True,
        conflicting_categories=(T, I),
        default_aggregation="sum",
        display_format="$#,##0.00",
    ),
    FieldDefinition(
        name="Revenue",
        category=M,
        expected_types=("numeric", "decimal", "float", "double", "real", "integer", "bigint", "money"),
        aliases=("total_revenue", "net_revenue", "revenue_amount", "total_amount", "gross_revenue"),
        description="Total revenue generated from completed orders.",
        is_forecastable=True,
        conflicting_categories=(T, I),
        default_aggregation="sum",
        display_format="$#,##0.00",
    ),
    FieldDefinition(
        name="Profit",
        category=M,
        expected_types=("numeric", "decimal", "float", "double", "real", "integer", "bigint", "money"),
        aliases=("net_profit", "profit_amount", "gross_profit", "margin_amount"),
        description="Net profit (Revenue minus Costs).",
        is_forecastable=True,
        conflicting_categories=(T, I),
        default_aggregation="sum",
        display_format="$#,##0.00",
    ),
    FieldDefinition(
        name="Discount",
        category=M,
        expected_types=("numeric", "decimal", "float", "double", "real"),
        aliases=("discount_amount", "discount_value", "discount_pct", "discount_percent", "discount_rate"),
        description="Discount applied to orders — can be a monetary amount or percentage.",
        is_forecastable=False,
        conflicting_categories=(T, I),
        default_aggregation="avg",
        display_format="0.0%",
    ),
    FieldDefinition(
        name="Quantity",
        category=M,
        expected_types=("integer", "bigint", "numeric", "decimal", "float"),
        aliases=("qty", "quantity_sold", "units_sold", "order_quantity", "quantity_ordered"),
        description="Number of units sold or ordered.",
        is_forecastable=True,
        conflicting_categories=(T, I),
        default_aggregation="sum",
        display_format="#,##0",
    ),
    FieldDefinition(
        name="Inventory",
        category=M,
        expected_types=("integer", "bigint", "numeric", "decimal"),
        aliases=("stock_quantity", "stock_level", "inventory_quantity", "on_hand", "stock_on_hand"),
        description="Current inventory / stock level.",
        is_forecastable=False,
        conflicting_categories=(T, I),
        default_aggregation="sum",
        display_format="#,##0",
    ),
    FieldDefinition(
        name="Cost",
        category=M,
        expected_types=("numeric", "decimal", "float", "double", "real", "money"),
        aliases=("cost_price", "unit_cost", "cogs", "cost_of_goods_sold", "purchase_cost"),
        description="Cost of goods sold or unit purchase cost.",
        is_forecastable=False,
        conflicting_categories=(T, I),
        default_aggregation="sum",
        display_format="$#,##0.00",
    ),
    FieldDefinition(
        name="Shipping Cost",
        category=M,
        expected_types=("numeric", "decimal", "float", "double", "real", "money"),
        aliases=("shipping_fee", "freight_cost", "delivery_cost", "postage"),
        description="Shipping or delivery cost charged per order.",
        is_forecastable=False,
        conflicting_categories=(T, I),
        default_aggregation="sum",
        display_format="$#,##0.00",
    ),

    # ------------------------------------------------------------------ #
    # DIMENSIONS
    # ------------------------------------------------------------------ #
    FieldDefinition(
        name="Region",
        category=D,
        expected_types=("varchar", "char", "text", "string"),
        aliases=("region_name", "sales_region", "geo_region", "territory", "area"),
        description="Geographic sales region or territory.",
        is_forecastable=False,
        conflicting_categories=(M, T),
        default_aggregation="count",
    ),
    FieldDefinition(
        name="Category",
        category=D,
        expected_types=("varchar", "char", "text", "string"),
        aliases=("product_category", "item_category", "main_category", "category_name"),
        description="Product or item category.",
        is_forecastable=False,
        conflicting_categories=(M, T),
        default_aggregation="count",
    ),
    FieldDefinition(
        name="Subcategory",
        category=D,
        expected_types=("varchar", "char", "text", "string"),
        aliases=("product_subcategory", "sub_category", "subcategory_name"),
        description="Product subcategory — more granular than Category.",
        is_forecastable=False,
        conflicting_categories=(M, T),
        default_aggregation="count",
    ),
    FieldDefinition(
        name="Segment",
        category=D,
        expected_types=("varchar", "char", "text", "string"),
        aliases=("customer_segment", "market_segment", "consumer_segment", "segment_name"),
        description="Customer or market segment.",
        is_forecastable=False,
        conflicting_categories=(M, T),
        default_aggregation="count",
    ),
    FieldDefinition(
        name="Payment Method",
        category=D,
        expected_types=("varchar", "char", "text", "string"),
        aliases=("payment_type", "payment_mode", "pay_method"),
        description="Payment method used (Credit Card, Cash, Online, etc.).",
        is_forecastable=False,
        conflicting_categories=(M, T),
        default_aggregation="count",
    ),
    FieldDefinition(
        name="Ship Mode",
        category=D,
        expected_types=("varchar", "char", "text", "string"),
        aliases=("shipping_mode", "delivery_mode", "ship_method", "shipping_class"),
        description="Shipping mode (Standard, Express, Same-Day, etc.).",
        is_forecastable=False,
        conflicting_categories=(M, T),
        default_aggregation="count",
    ),
    FieldDefinition(
        name="Status",
        category=D,
        expected_types=("varchar", "char", "text", "string"),
        aliases=("order_status", "item_status", "shipment_status", "fulfillment_status"),
        description="Order or item status (Pending, Shipped, Delivered, Returned, etc.).",
        is_forecastable=False,
        conflicting_categories=(M, T),
        default_aggregation="count",
    ),

    # ------------------------------------------------------------------ #
    # TEMPORAL
    # ------------------------------------------------------------------ #
    FieldDefinition(
        name="Order Date",
        category=T,
        expected_types=("date", "timestamp", "timestamptz", "datetime", "timestamp with time zone",
                        "timestamp without time zone"),
        aliases=("order_date", "purchase_date", "sale_date", "transaction_date", "created_date",
                 "created_at", "order_time"),
        description="Date the order was placed.",
        is_forecastable=False,
        conflicting_categories=(M, I),
        default_aggregation="count",
        display_format="YYYY-MM-DD",
    ),
    FieldDefinition(
        name="Ship Date",
        category=T,
        expected_types=("date", "timestamp", "timestamptz", "datetime", "timestamp with time zone",
                        "timestamp without time zone"),
        aliases=("ship_date", "shipment_date", "dispatch_date", "shipped_at", "shipped_date"),
        description="Date the order was shipped.",
        is_forecastable=False,
        conflicting_categories=(M, I),
        default_aggregation="count",
        display_format="YYYY-MM-DD",
    ),

    # ------------------------------------------------------------------ #
    # IDENTIFIERS
    # ------------------------------------------------------------------ #
    FieldDefinition(
        name="Customer",
        category=I,
        expected_types=("varchar", "char", "text", "integer", "bigint", "uuid"),
        aliases=("customer_id", "client_id", "customer_name", "user_id", "buyer_id"),
        description="Customer identifier — ID or name column.",
        is_forecastable=False,
        conflicting_categories=(M,),
        default_aggregation="count",
    ),
    FieldDefinition(
        name="Product",
        category=I,
        expected_types=("varchar", "char", "text", "integer", "bigint", "uuid"),
        aliases=("product_id", "item_id", "sku", "product_name", "item_name"),
        description="Product identifier — ID or name column.",
        is_forecastable=False,
        conflicting_categories=(M,),
        default_aggregation="count",
    ),
    FieldDefinition(
        name="Order ID",
        category=I,
        expected_types=("varchar", "char", "text", "integer", "bigint", "uuid"),
        aliases=("order_id", "transaction_id", "invoice_id", "order_number", "order_ref"),
        description="Unique order identifier.",
        is_forecastable=False,
        conflicting_categories=(M,),
        default_aggregation="count",
    ),
    FieldDefinition(
        name="Supplier",
        category=I,
        expected_types=("varchar", "char", "text", "integer", "bigint"),
        aliases=("supplier_id", "vendor_id", "supplier_name", "vendor_name"),
        description="Supplier or vendor identifier.",
        is_forecastable=False,
        conflicting_categories=(M,),
        default_aggregation="count",
    ),
]
