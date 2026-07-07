"""
BusinessLens AI — DataQualityReport ORM Model

Stores the result of a data quality scan for a connection.
Linked to a SchemaSnapshot (quality is computed from snapshot data).
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Float
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, TenantMixin, generate_uuid


class DataQualityReport(Base, TenantMixin, TimestampMixin):
    """
    Data quality assessment for a connection snapshot.

    overall_score: 0-100 composite score
    table_scores: {table_name: {score, issues: [{column, rule, severity, value}]}}
    """

    __tablename__ = "data_quality_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    connection_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False, index=True
    )
    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False, index=True
    )

    overall_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    table_scores: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    # Aggregate counts
    total_issues: Mapped[int] = mapped_column(nullable=False, default=0)
    critical_issues: Mapped[int] = mapped_column(nullable=False, default=0)
    warning_issues: Mapped[int] = mapped_column(nullable=False, default=0)
    info_issues: Mapped[int] = mapped_column(nullable=False, default=0)

    is_latest: Mapped[bool] = mapped_column(nullable=False, default=True, index=True)

    def __repr__(self) -> str:
        return (
            f"<DataQualityReport connection={self.connection_id} "
            f"score={self.overall_score:.1f}>"
        )
