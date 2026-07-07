"""
BusinessLens AI — BackgroundJob ORM Model

Tracks asynchronous operations: schema scans, report generation, forecasting.
Clients poll the status endpoint until COMPLETED or FAILED.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, TenantMixin, generate_uuid


class JobStatus(str):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class JobType(str):
    SCHEMA_SCAN = "schema_scan"
    METADATA_EXTRACTION = "metadata_extraction"
    DATA_QUALITY = "data_quality"
    REPORT_EXPORT = "report_export"
    FORECAST = "forecast"


class BackgroundJob(Base, TenantMixin, TimestampMixin):
    __tablename__ = "background_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    job_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default=JobStatus.PENDING, index=True
    )
    progress_message: Mapped[str | None] = mapped_column(String(512), nullable=True)
    result_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<BackgroundJob type={self.job_type} status={self.status}>"
