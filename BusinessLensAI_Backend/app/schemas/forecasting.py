"""
BusinessLens AI — Forecasting Schemas
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class ForecastRequest(BaseModel):
    metric_field: str = Field(..., description="Business field name to forecast (must be numeric metric)")
    date_field: str = Field(..., description="Temporal business field name for time axis")
    horizon: int = Field(12, ge=1, le=104, description="Number of future periods to predict")
    time_grain: str = Field("month", description="day, week, month, quarter")
    confidence_level: float = Field(0.95, description="0.80 or 0.95")


class ForecastDataPoint(BaseModel):
    timestamp: str
    predicted_value: float
    lower_bound: float
    upper_bound: float
    is_historical: bool = False


class ForecastResponse(BaseModel):
    metric_field: str
    date_field: str
    time_grain: str
    horizon: int
    model_used: str  # AutoARIMA, ETS, CES, or LinearTrendFallback
    historical_points: list[ForecastDataPoint]
    forecast_points: list[ForecastDataPoint]
    trend_summary: str
    seasonality_detected: bool
