"""
BusinessLens AI — Dashboard & Widget ORM Models
"""

from __future__ import annotations

import uuid
from sqlalchemy import Boolean, Integer, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin, TimestampMixin, generate_uuid


class Dashboard(Base, TenantMixin, TimestampMixin):
    """
    A BI dashboard persisted for a connection.
    Can be auto-generated from domain templates or custom created by users.
    """
    __tablename__ = "dashboards"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    connection_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    layout_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_by: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)

    widgets: Mapped[list[DashboardWidget]] = relationship(
        "DashboardWidget", back_populates="dashboard", cascade="all, delete-orphan", order_by="DashboardWidget.position"
    )


class DashboardWidget(Base, TimestampMixin):
    """
    A single widget on a dashboard.
    query_config stores an AnalyticsQueryRequest dict so the widget renders dynamically via AnalyticsEngine.
    """
    __tablename__ = "dashboard_widgets"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    dashboard_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("dashboards.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    widget_type: Mapped[str] = mapped_column(String(64), nullable=False)  # kpi_card, line_chart, bar_chart, pie_chart, table
    query_config: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    width_span: Mapped[int] = mapped_column(Integer, nullable=False, default=6)  # 1 to 12 grid span

    dashboard: Mapped[Dashboard] = relationship("Dashboard", back_populates="widgets")
