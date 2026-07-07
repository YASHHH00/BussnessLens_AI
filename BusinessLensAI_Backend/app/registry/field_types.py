"""
BusinessLens AI — Field Category Enum

Defines the four fundamental roles a business field can play in analytics.
Used by: registry validation, mapping validation, semantic layer, analytics engine.
"""

from __future__ import annotations

from enum import StrEnum


class FieldCategory(StrEnum):
    """
    Categorical classification of a business field.

    METRIC:     Numeric, aggregatable values (Sales, Profit, Revenue, Discount, Quantity)
    DIMENSION:  Categorical grouping keys (Region, Category, Product, Payment Method)
    TEMPORAL:   Date/time axes (Order Date, Ship Date, Created At)
    IDENTIFIER: Entity keys — typically PK/FK columns (Customer ID, Product ID, Order ID)
    """
    METRIC = "metric"
    DIMENSION = "dimension"
    TEMPORAL = "temporal"
    IDENTIFIER = "identifier"
