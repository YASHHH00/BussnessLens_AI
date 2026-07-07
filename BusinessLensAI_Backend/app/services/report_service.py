"""
BusinessLens AI — Report Service
"""

from __future__ import annotations

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import AuditAction, emit_audit_log
from app.engines.report_generator import ReportGeneratorEngine
from app.registry.field_registry import BusinessFieldRegistry
from app.schemas.analytics import AnalyticsQueryRequest
from app.schemas.reports import ReportExportRequest
from app.services.analytics_service import AnalyticsService


class ReportService:
    def __init__(self, db: AsyncSession, registry: BusinessFieldRegistry) -> None:
        self._db = db
        self._analytics_svc = AnalyticsService(db, registry)
        self._engine = ReportGeneratorEngine()

    async def export_excel(
        self,
        connection_id: UUID,
        organization_id: UUID,
        user_id: UUID,
        request: ReportExportRequest,
    ) -> bytes:
        kpis = await self._analytics_svc.evaluate_kpis(connection_id, organization_id)
        kpi_dicts = [
            {"display_name": k.display_name, "formatted_value": k.formatted_value, "unit": k.unit or ""}
            for k in kpis
        ]

        data_rows = []
        if request.include_raw_data and kpis:
            # Query top metrics
            metrics = [k.kpi_name for k in kpis[:3]]
            try:
                res = await self._analytics_svc.execute_query(
                    connection_id,
                    organization_id,
                    AnalyticsQueryRequest(metrics=metrics, limit=100),
                )
                data_rows = res.rows
            except Exception:
                pass

        xlsx_bytes = self._engine.build_excel_report(request.title, kpi_dicts, data_rows)

        await emit_audit_log(
            db=self._db,
            action=AuditAction.REPORT_EXPORTED,
            user_id=user_id,
            organization_id=organization_id,
            resource_type="report",
            details={"title": request.title, "format": "xlsx"},
        )

        return xlsx_bytes
