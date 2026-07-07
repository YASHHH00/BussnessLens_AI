"""
BusinessLens AI — Cache Key Generation Helpers

All cache keys are generated through this module — never constructed ad-hoc.
This ensures consistent namespacing, easy invalidation, and no typos.
"""

from __future__ import annotations

import hashlib
import json
from uuid import UUID


class CacheKeys:
    """
    Static factory for all cache key strings.

    Naming convention: biz:{domain}:{connection_id}:{detail}
    The `biz:` prefix namespaces our keys in a shared Redis instance.
    """

    @staticmethod
    def _hash(data: dict | list | str) -> str:
        """Create a short deterministic hash from any serializable data."""
        if isinstance(data, str):
            raw = data
        else:
            raw = json.dumps(data, sort_keys=True, default=str)
        return hashlib.md5(raw.encode()).hexdigest()[:12]

    # ------------------------------------------------------------------ #
    # Dashboard & Widget Queries
    # ------------------------------------------------------------------ #
    @staticmethod
    def dashboard_query(
        connection_id: UUID, widget_id: UUID, filters: dict | None = None
    ) -> str:
        filters_hash = CacheKeys._hash(filters or {})
        return f"biz:dash:{connection_id}:{widget_id}:{filters_hash}"

    # ------------------------------------------------------------------ #
    # KPI Results
    # ------------------------------------------------------------------ #
    @staticmethod
    def kpi_result(
        connection_id: UUID,
        kpi_name: str,
        date_range: dict | None = None,
        filters: dict | None = None,
    ) -> str:
        params_hash = CacheKeys._hash({**(date_range or {}), **(filters or {})})
        return f"biz:kpi:{connection_id}:{kpi_name}:{params_hash}"

    # ------------------------------------------------------------------ #
    # AI Schema Analysis
    # ------------------------------------------------------------------ #
    @staticmethod
    def ai_schema_analysis(connection_id: UUID, schema_hash: str) -> str:
        return f"biz:ai:schema:{connection_id}:{schema_hash}"

    # ------------------------------------------------------------------ #
    # Dashboard Recommendations
    # ------------------------------------------------------------------ #
    @staticmethod
    def dashboard_recommendations(connection_id: UUID, mapping_hash: str) -> str:
        return f"biz:rec:{connection_id}:{mapping_hash}"

    # ------------------------------------------------------------------ #
    # Semantic Context
    # ------------------------------------------------------------------ #
    @staticmethod
    def semantic_context(connection_id: UUID, mapping_set_id: UUID | None = None) -> str:
        suffix = str(mapping_set_id) if mapping_set_id else "latest"
        return f"biz:sem:{connection_id}:{suffix}"

    # ------------------------------------------------------------------ #
    # Rules Engine (for caching rule evaluation results)
    # ------------------------------------------------------------------ #
    @staticmethod
    def rules_evaluation(
        connection_id: UUID, date_range: dict | None = None
    ) -> str:
        h = CacheKeys._hash(date_range or {})
        return f"biz:rules:{connection_id}:{h}"

    # ------------------------------------------------------------------ #
    # Invalidation Patterns (glob)
    # ------------------------------------------------------------------ #
    @staticmethod
    def connection_pattern(connection_id: UUID) -> str:
        """Glob matching ALL keys for a connection — use for bulk invalidation."""
        return f"biz:*:{connection_id}:*"

    @staticmethod
    def dashboard_pattern(dashboard_id: UUID) -> str:
        return f"biz:dash:*:{dashboard_id}:*"

    @staticmethod
    def kpi_pattern(connection_id: UUID) -> str:
        return f"biz:kpi:{connection_id}:*"
