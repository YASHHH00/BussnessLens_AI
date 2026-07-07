"""
BusinessLens AI — Centralized Audit Log Emitter

Every significant operation (login, mapping save, dashboard update, etc.)
emits a structured audit record. Audit writes are fire-and-forget
(non-blocking) to avoid impacting request latency.

Usage:
    from app.core.audit import emit_audit_log, AuditAction

    await emit_audit_log(
        db=db,
        action=AuditAction.MAPPING_SAVED,
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        resource_type="mapping_set",
        resource_id=mapping_set.id,
        details={"fields_mapped": 5},
        ip_address=request.client.host,
    )
"""

from __future__ import annotations

import asyncio
from enum import StrEnum
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


# ------------------------------------------------------------------ #
# Audit Action Enum
# ------------------------------------------------------------------ #

class AuditAction(StrEnum):
    # Auth
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_REGISTER = "user.register"
    USER_LOGIN_FAILED = "user.login_failed"
    USER_LOCKED = "user.locked"

    # Connections
    CONNECTION_CREATED = "connection.created"
    CONNECTION_TESTED = "connection.tested"
    CONNECTION_DELETED = "connection.deleted"

    # Schema
    SCHEMA_SCAN_STARTED = "schema.scan_started"
    SCHEMA_SCAN_COMPLETED = "schema.scan_completed"

    # Mappings
    MAPPING_SAVED = "mapping.saved"
    MAPPING_UPDATED = "mapping.updated"

    # Dashboards
    DASHBOARD_GENERATED = "dashboard.generated"
    DASHBOARD_UPDATED = "dashboard.updated"
    DASHBOARD_ROLLBACK = "dashboard.rollback"

    # Forecasting
    FORECAST_REQUESTED = "forecast.requested"

    # AI Assistant
    AI_QUERY_SUBMITTED = "assistant.query"

    # Reports
    REPORT_EXPORTED = "report.exported"

    # Admin
    ADMIN_USER_CREATED = "admin.user_created"
    ADMIN_USER_UPDATED = "admin.user_updated"
    ADMIN_USER_DEACTIVATED = "admin.user_deactivated"

    # SQL Playground
    SQL_PLAYGROUND_EXECUTED = "sql_playground.executed"

    # Cache
    CACHE_INVALIDATED = "cache.invalidated"

    # Theme
    THEME_CHANGED = "user.theme_changed"


# ------------------------------------------------------------------ #
# Emit Function
# ------------------------------------------------------------------ #

async def emit_audit_log(
    db: AsyncSession,
    action: AuditAction,
    user_id: UUID,
    organization_id: UUID,
    resource_type: str,
    resource_id: UUID | None = None,
    details: dict[str, Any] | None = None,
    ip_address: str | None = None,
) -> None:
    """
    Write an audit log record to the database.

    This is intentionally non-blocking — exceptions are caught and logged
    so that audit failures never break the primary operation.

    If AUDIT_LOG_ENABLED=False in config, this is a no-op.
    """
    if not settings.AUDIT_LOG_ENABLED:
        return

    try:
        # Import here to avoid circular imports at module load time
        from app.models.audit_log import AuditLog

        log_entry = AuditLog(
            action=action,
            user_id=user_id,
            organization_id=organization_id,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
        )
        db.add(log_entry)
        # We use flush (not commit) — the outer service transaction owns the commit.
        # This ensures audit log is atomic with the business operation.
        await db.flush([log_entry])

    except Exception:
        # Audit failures must NEVER crash the primary operation
        logger.exception(
            "Audit log write failed (action=%s, user=%s) — "
            "primary operation will continue.",
            action,
            user_id,
        )
