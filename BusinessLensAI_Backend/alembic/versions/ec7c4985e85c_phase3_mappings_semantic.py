"""phase3_mappings_semantic

Phase 3 tables: mapping_sets, field_mappings, smart_mapping_memory

Revision ID: ec7c4985e85c
Revises: b6e82daf4ade
Create Date: 2026-07-03
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "ec7c4985e85c"
down_revision: str | None = "b6e82daf4ade"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # mapping_sets
    # ------------------------------------------------------------------ #
    op.create_table(
        "mapping_sets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("connection_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("snapshot_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="draft"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("ai_domain_fit_score", sa.Float(), nullable=True),
        sa.Column("ai_analyst_notes", sa.Text(), nullable=True),
        sa.Column("ai_suggested_primary_table", sa.String(256), nullable=True),
        sa.Column("join_hints", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("confirmed_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("confirmed_at", sa.String(64), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_mapping_sets_organization_id", "mapping_sets", ["organization_id"])
    op.create_index("ix_mapping_sets_connection_id", "mapping_sets", ["connection_id"])
    op.create_index("ix_mapping_sets_status", "mapping_sets", ["status"])
    op.create_index("ix_mapping_sets_is_active", "mapping_sets", ["is_active"])

    # ------------------------------------------------------------------ #
    # field_mappings
    # ------------------------------------------------------------------ #
    op.create_table(
        "field_mappings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("mapping_set_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("table_name", sa.String(256), nullable=False),
        sa.Column("column_name", sa.String(256), nullable=False),
        sa.Column("physical_type", sa.String(64), nullable=False, server_default="varchar"),
        sa.Column("business_field", sa.String(128), nullable=True),
        sa.Column("ai_confidence", sa.Float(), nullable=True),
        sa.Column("ai_reasoning", sa.Text(), nullable=True),
        sa.Column("ai_alternatives", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("is_user_overridden", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("user_override_note", sa.Text(), nullable=True),
        sa.Column("is_validated", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("validation_errors", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("mapping_set_id", "table_name", "column_name", name="uq_field_mapping_col_per_set"),
    )
    op.create_index("ix_field_mappings_mapping_set_id", "field_mappings", ["mapping_set_id"])

    # ------------------------------------------------------------------ #
    # smart_mapping_memory
    # ------------------------------------------------------------------ #
    op.create_table(
        "smart_mapping_memory",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("column_name_normalized", sa.String(256), nullable=False),
        sa.Column("original_examples", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("business_field", sa.String(128), nullable=False),
        sa.Column("physical_type", sa.String(64), nullable=True),
        sa.Column("confirm_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("avg_confidence", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("organization_id", "column_name_normalized", "business_field", name="uq_memory_org_col_field"),
    )
    op.create_index("ix_smart_mapping_memory_column_name_normalized", "smart_mapping_memory", ["column_name_normalized"])
    op.create_index("ix_smart_mapping_memory_organization_id", "smart_mapping_memory", ["organization_id"])

    # updated_at triggers
    for table in ("mapping_sets", "field_mappings", "smart_mapping_memory"):
        op.execute(
            f"""
            CREATE TRIGGER set_updated_at_{table}
            BEFORE UPDATE ON {table}
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            """
        )


def downgrade() -> None:
    for table in ("mapping_sets", "field_mappings", "smart_mapping_memory"):
        op.execute(f"DROP TRIGGER IF EXISTS set_updated_at_{table} ON {table}")
    op.drop_table("smart_mapping_memory")
    op.drop_table("field_mappings")
    op.drop_table("mapping_sets")
