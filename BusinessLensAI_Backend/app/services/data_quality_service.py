"""
BusinessLens AI — Data Quality Service
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.engines.data_quality_engine import DataQualityEngine
from app.models.data_quality import DataQualityReport
from app.repositories.schema_repository import SchemaRepository
from app.repositories.base import BaseRepository
from app.models.data_quality import DataQualityReport
from app.core.exceptions import NotFoundError
from app.schemas.data_quality import DataQualityReportResponse, TableQualityScore, DataQualityIssue


class DataQualityRepository(BaseRepository[DataQualityReport]):
    model_class = DataQualityReport


class DataQualityService:
    def __init__(self, db: AsyncSession) -> None:
        self._schema_repo = SchemaRepository(db)
        self._dq_repo = DataQualityRepository(db)
        self._db = db
        self._engine = DataQualityEngine()

    async def run_quality_check(
        self,
        connection_id: UUID,
        organization_id: UUID,
    ) -> DataQualityReportResponse:
        """
        Run data quality evaluation against the latest schema snapshot.
        """
        snapshot = await self._schema_repo.get_latest_for_connection(
            connection_id, organization_id
        )
        if not snapshot:
            raise NotFoundError("SchemaSnapshot", connection_id)

        result = self._engine.evaluate_snapshot(snapshot.tables_json)

        # Mark existing as non-latest (use SQLAlchemy update)
        from sqlalchemy import update
        await self._db.execute(
            update(DataQualityReport)
            .where(DataQualityReport.connection_id == connection_id)
            .values(is_latest=False)
        )

        report = DataQualityReport(
            connection_id=connection_id,
            snapshot_id=snapshot.id,
            organization_id=organization_id,
            overall_score=result["overall_score"],
            table_scores=result["table_scores"],
            total_issues=result["total_issues"],
            critical_issues=result["critical_issues"],
            warning_issues=result["warning_issues"],
            info_issues=result["info_issues"],
            is_latest=True,
        )
        report = await self._dq_repo.create(report)

        return self._to_response(report)

    def _to_response(self, report: DataQualityReport) -> DataQualityReportResponse:
        table_scores = []
        for table_name, data in report.table_scores.items():
            issues = [DataQualityIssue(**i) for i in data.get("issues", [])]
            table_scores.append(
                TableQualityScore(table=table_name, score=data["score"], issues=issues)
            )
        return DataQualityReportResponse(
            id=report.id,
            connection_id=report.connection_id,
            snapshot_id=report.snapshot_id,
            overall_score=report.overall_score,
            total_issues=report.total_issues,
            critical_issues=report.critical_issues,
            warning_issues=report.warning_issues,
            info_issues=report.info_issues,
            table_scores=table_scores,
            created_at=report.created_at,
        )
