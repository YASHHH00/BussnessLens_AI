"""
BusinessLens AI — v1 Aggregated Router
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.connections import router as connections_router
from app.api.v1.schema_detection import router as schema_router
from app.api.v1.data_quality import router as data_quality_router
from app.api.v1.mappings import router as mappings_router
from app.api.v1.semantic import router as semantic_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.dashboards import router as dashboards_router
from app.api.v1.insights import router as insights_router
from app.api.v1.forecasting import router as forecast_router
from app.api.v1.assistant import router as assistant_router
from app.api.v1.sql_playground import router as playground_router
from app.api.v1.reports import router as reports_router
from app.api.v1.admin import router as admin_router
from app.api.v1.audit import router as audit_router
from app.api.v1.explainability import router as explain_router

router = APIRouter(prefix="/api/v1")

router.include_router(auth_router)
router.include_router(users_router)
router.include_router(connections_router)
router.include_router(schema_router)
router.include_router(data_quality_router)
router.include_router(mappings_router)
router.include_router(semantic_router)
router.include_router(analytics_router)
router.include_router(dashboards_router)
router.include_router(insights_router)
router.include_router(forecast_router)
router.include_router(assistant_router)
router.include_router(playground_router)
router.include_router(reports_router)
router.include_router(admin_router)
router.include_router(audit_router)
router.include_router(explain_router)

