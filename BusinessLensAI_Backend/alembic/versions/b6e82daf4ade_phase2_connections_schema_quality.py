"""phase2_connections_schema_quality

Phase 2 tables: db_connections, schema_snapshots, data_quality_reports

Revision ID: b6e82daf4ade
Revises: d62460f0881b
Create Date: 2026-07-03
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "b6e82daf4ade"
down_revision: str | None = "d62460f0881b"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # db_connections
    # ------------------------------------------------------------------ #
    op.create_table(
        "db_connections",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("description", sa.String(1024), nullable=True),
        sa.Column("connection_type", sa.String(32), nullable=False),
        sa.Column("host", sa.String(512), nullable=True),
        sa.Column("port", sa.Integer(), nullable=True),
        sa.Column("database", sa.String(256), nullable=True),
        sa.Column("username", sa.String(256), nullable=True),
        sa.Column("encrypted_password", sa.String(1024), nullable=True),
        sa.Column("ssl_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("file_path", sa.String(1024), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("last_tested_at", sa.String(64), nullable=True),
        sa.Column("last_test_succeeded", sa.Boolean(), nullable=True),
        sa.Column("schema_version_hash", sa.String(64), nullable=True),
        sa.Column("extra_params", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_db_connections_organization_id", "db_connections", ["organization_id"])
    op.create_index("ix_db_connections_connection_type", "db_connections", ["connection_type"])

    # ------------------------------------------------------------------ #
    # schema_snapshots
    # ------------------------------------------------------------------ #
    op.create_table(
        "schema_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("connection_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tables_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("table_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("column_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("schema_hash", sa.String(64), nullable=False),
        sa.Column("scan_duration_ms", sa.Integer(), nullable=True),
        sa.Column("scan_error", sa.Text(), nullable=True),
        sa.Column("is_latest", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_schema_snapshots_connection_id", "schema_snapshots", ["connection_id"])
    op.create_index("ix_schema_snapshots_organization_id", "schema_snapshots", ["organization_id"])
    op.create_index("ix_schema_snapshots_schema_hash", "schema_snapshots", ["schema_hash"])
    op.create_index("ix_schema_snapshots_is_latest", "schema_snapshots", ["is_latest"])

    # ------------------------------------------------------------------ #
    # data_quality_reports
    # ------------------------------------------------------------------ #
    op.create_table(
        "data_quality_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("connection_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("snapshot_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("overall_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("table_scores", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("total_issues", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("critical_issues", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("warning_issues", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("info_issues", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_latest", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_data_quality_reports_connection_id", "data_quality_reports", ["connection_id"])
    op.create_index("ix_data_quality_reports_snapshot_id", "data_quality_reports", ["snapshot_id"])
    op.create_index("ix_data_quality_reports_is_latest", "data_quality_reports", ["is_latest"])

    # updated_at triggers
    for table in ("db_connections", "schema_snapshots", "data_quality_reports"):
        op.execute(
            f"""
            CREATE TRIGGER set_updated_at_{table}
            BEFORE UPDATE ON {table}
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            """
        )


def downgrade() -> None:
    for table in ("db_connections", "schema_snapshots", "data_quality_reports"):
        op.execute(f"DROP TRIGGER IF EXISTS set_updated_at_{table} ON {table}")
    op.drop_table("data_quality_reports")
    op.drop_table("schema_snapshots")
    op.drop_table("db_connections")
