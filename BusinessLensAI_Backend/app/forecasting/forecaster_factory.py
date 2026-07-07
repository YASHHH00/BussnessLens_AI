"""app/forecasting/forecaster_factory.py — Stub (Phase 5 will complete this)"""
from __future__ import annotations
from app.core.config import settings
from app.core.logging_config import get_logger
logger = get_logger(__name__)

class ForecasterFactory:
    def create(self):
        logger.info("Forecasting provider: %s (stub — Phase 5)", settings.FORECAST_PROVIDER)
        return None
