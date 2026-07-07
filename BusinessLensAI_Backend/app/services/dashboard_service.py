"""
BusinessLens AI — Dashboard Service

CRUD for Dashboards and auto-generation from domain templates against SemanticContext.
"""

from __future__ import annotations

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import AuditAction, emit_audit_log
from app.core.exceptions import NotFoundError, ValidationError
from app.models.dashboard import Dashboard, DashboardWidget
from app.repositories.connection_repository import ConnectionRepository
from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.dashboard import DashboardCreateRequest, DashboardResponse
from app.semantic.semantic_layer import SemanticLayer


class DashboardService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._repo = DashboardRepository(db)
        self._conn_repo = ConnectionRepository(db)
        self._semantic_layer = SemanticLayer(db)

    async def list_dashboards(self, connection_id: UUID, organization_id: UUID) -> list[DashboardResponse]:
        await self._conn_repo.get_by_id_or_raise(connection_id, organization_id, "Connection")
        dashboards = await self._repo.list_for_connection(connection_id, organization_id)
        return [DashboardResponse.model_validate(d) for d in dashboards]

    async def get_dashboard(self, dashboard_id: UUID, organization_id: UUID) -> DashboardResponse:
        d = await self._repo.get_with_widgets(dashboard_id, organization_id)
        if not d:
            raise NotFoundError("Dashboard", dashboard_id)
        return DashboardResponse.model_validate(d)

    async def create_dashboard(
        self,
        connection_id: UUID,
        organization_id: UUID,
        user_id: UUID,
        req: DashboardCreateRequest,
    ) -> DashboardResponse:
        await self._conn_repo.get_by_id_or_raise(connection_id, organization_id, "Connection")

        if req.is_default:
            # If setting as default, un-default others
            existing = await self._repo.list_for_connection(connection_id, organization_id)
            for d in existing:
                if d.is_default:
                    d.is_default = False

        dashboard = Dashboard(
            connection_id=connection_id,
            organization_id=organization_id,
            name=req.name,
            description=req.description,
            is_default=req.is_default,
            created_by=user_id,
        )

        widgets = []
        for idx, w_req in enumerate(req.widgets):
            widgets.append(
                DashboardWidget(
                    title=w_req.title,
                    widget_type=w_req.widget_type,
                    query_config=w_req.query_config,
                    position=w_req.position or idx,
                    width_span=w_req.width_span,
                )
            )
        dashboard.widgets = widgets

        created = await self._repo.create(dashboard)
        await emit_audit_log(
            db=self._db,
            action=AuditAction.DASHBOARD_CREATED,
            user_id=user_id,
            organization_id=organization_id,
            resource_type="dashboard",
            resource_id=created.id,
            details={"name": created.name, "widgets_count": len(widgets)},
        )

        return DashboardResponse.model_validate(created)

    async def auto_generate_dashboards(
        self,
        connection_id: UUID,
        organization_id: UUID,
        user_id: UUID,
    ) -> list[DashboardResponse]:
        """
        Auto-generate domain dashboards based on SemanticContext field availability.
        Loads RETAIL_TEMPLATES (or active plugin templates) and creates matching dashboards.
        """
        await self._conn_repo.get_by_id_or_raise(connection_id, organization_id, "Connection")
        context = await self._semantic_layer.get_context(connection_id, organization_id)

        from app.plugins.domains.retail.templates import RETAIL_TEMPLATES

        # Delete any previously auto-generated dashboards if desired or just append
        existing = await self._repo.list_for_connection(connection_id, organization_id)
        if not existing:
            created_list = []
            for tpl in RETAIL_TEMPLATES:
                missing = [f for f in tpl.required_fields if not context.has_field(f)]
                if missing:
                    continue

                dashboard = Dashboard(
                    connection_id=connection_id,
                    organization_id=organization_id,
                    name=tpl.display_name,
                    description=tpl.description,
                    is_default=tpl.is_default,
                    created_by=user_id,
                )

                widgets = []
                for idx, w_tpl in enumerate(tpl.widgets):
                    # Determine query config
                    metrics = [w_tpl.metric] if w_tpl.metric else (tpl.required_fields[:1])
                    if w_tpl.kpi_name:
                        # Map kpi name to required metric
                        metrics = [tpl.required_fields[0]]
                    dimensions = [w_tpl.group_by] if w_tpl.group_by else []

                    query_cfg = {
                        "metrics": [m for m in metrics if m],
                        "dimensions": [d for d in dimensions if d],
                        "limit": 50,
                    }

                    widgets.append(
                        DashboardWidget(
                            title=w_tpl.title,
                            widget_type=w_tpl.widget_type,
                            query_config=query_cfg,
                            position=idx,
                            width_span=6 if w_tpl.widget_type in ("line_chart", "bar_chart") else 3,
                        )
                    )

                dashboard.widgets = widgets
                created = await self._repo.create(dashboard)
                created_list.append(DashboardResponse.model_validate(created))

            if created_list:
                await emit_audit_log(
                    db=self._db,
                    action=AuditAction.DASHBOARD_CREATED,
                    user_id=user_id,
                    organization_id=organization_id,
                    resource_type="dashboard",
                    resource_id=created_list[0].id,
                    details={"auto_generated": len(created_list)},
                )
            return created_list

        return [DashboardResponse.model_validate(d) for d in existing]

    async def delete_dashboard(self, dashboard_id: UUID, organization_id: UUID, user_id: UUID) -> None:
        dashboard = await self._repo.get_by_id_or_raise(dashboard_id, organization_id, "Dashboard")
        await self._repo.delete(dashboard)
        await emit_audit_log(
            db=self._db,
            action=AuditAction.DASHBOARD_DELETED,
            user_id=user_id,
            organization_id=organization_id,
            resource_type="dashboard",
            resource_id=dashboard_id,
            details={"name": dashboard.name},
        )
