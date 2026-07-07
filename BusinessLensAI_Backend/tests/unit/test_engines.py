"""
BusinessLens AI — Unit Tests for Core Engines
"""

import pytest
from app.engines.analytics_engine import AnalyticsEngine
from app.engines.forecasting_engine import ForecastingEngine
from app.engines.sql_playground_engine import SQLPlaygroundEngine
from app.registry.field_registry import BusinessFieldRegistry
from app.schemas.analytics import AnalyticsQueryRequest
from app.schemas.forecasting import ForecastRequest
from app.core.exceptions import ValidationError


def test_analytics_engine_quote_ident():
    registry = BusinessFieldRegistry()
    engine = AnalyticsEngine(registry)
    assert engine._quote_ident("orders", "postgres") == '"orders"'
    assert engine._quote_ident("orders", "mysql") == '`orders`'


def test_forecasting_engine_ols():
    engine = ForecastingEngine()
    req = ForecastRequest(
        metric_field="Revenue",
        date_field="Order Date",
        horizon=3,
        time_grain="month",
    )
    hist_rows = [
        {"Order Date": "2026-01-01", "Revenue": 100.0},
        {"Order Date": "2026-02-01", "Revenue": 110.0},
        {"Order Date": "2026-03-01", "Revenue": 120.0},
        {"Order Date": "2026-04-01", "Revenue": 130.0},
    ]
    resp = engine.compute_forecast(req, hist_rows)
    assert resp.metric_field == "Revenue"
    assert len(resp.historical_points) == 4
    assert len(resp.forecast_points) == 3
    # With exact slope 10.0, step 1 (pred_x=4) predicted value should be ~140.0
    assert abs(resp.forecast_points[0].predicted_value - 140.0) < 0.1


@pytest.mark.asyncio
async def test_sql_playground_engine_validation():
    engine = SQLPlaygroundEngine()

    # Reject write query
    with pytest.raises(ValidationError, match="Only read-only SELECT or EXPLAIN queries are permitted"):
        await engine.execute_readonly(None, "DELETE FROM orders WHERE id=1")

    # Reject non-SELECT
    with pytest.raises(ValidationError, match="Query must begin with SELECT, WITH, or EXPLAIN"):
        await engine.execute_readonly(None, "SHOW TABLES")
