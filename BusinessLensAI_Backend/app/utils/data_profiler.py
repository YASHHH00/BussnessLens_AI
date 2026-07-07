"""
BusinessLens AI — Data Profiler

Computes column-level statistics from schema snapshot data.
Feeds the DataQualityEngine with null rates, uniqueness, type compliance, etc.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ColumnProfile:
    table: str
    column: str
    physical_type: str
    row_count: int
    null_count: int
    null_pct: float
    unique_count: int
    unique_pct: float
    sample_values: list[Any]
    min_value: Any = None
    max_value: Any = None
    mean_value: float | None = None


def profile_column_from_snapshot(
    table_name: str,
    column_meta: dict,
    table_row_count: int,
    sample_values: list[Any],
) -> ColumnProfile:
    """
    Build a ColumnProfile from snapshot metadata.
    For deeper stats (mean, exact null count) we rely on what
    the connector collected during schema scan.
    """
    non_null = [v for v in sample_values if v is not None]
    null_count_estimate = table_row_count - len(non_null)  # rough from sample
    null_pct = null_count_estimate / max(table_row_count, 1)
    unique_count = len(set(str(v) for v in non_null))
    unique_pct = unique_count / max(len(non_null), 1)

    numeric_vals = []
    for v in non_null:
        try:
            numeric_vals.append(float(v))
        except (TypeError, ValueError):
            pass

    return ColumnProfile(
        table=table_name,
        column=column_meta.get("name", ""),
        physical_type=column_meta.get("physical_type", "varchar"),
        row_count=table_row_count,
        null_count=null_count_estimate,
        null_pct=null_pct,
        unique_count=unique_count,
        unique_pct=unique_pct,
        sample_values=sample_values,
        min_value=min(numeric_vals) if numeric_vals else None,
        max_value=max(numeric_vals) if numeric_vals else None,
        mean_value=sum(numeric_vals) / len(numeric_vals) if numeric_vals else None,
    )


def compute_schema_hash(tables_json: dict) -> str:
    """
    Compute a deterministic SHA-256 hash of the schema structure.
    Used to detect schema drift between snapshots.
    """
    import hashlib
    import json

    # Only hash structural metadata (names, types) — not sample values
    structural = {}
    for table_name in sorted(tables_json.keys()):
        structural[table_name] = sorted(
            [
                {"name": c["name"], "type": c.get("physical_type", "")}
                for c in tables_json[table_name].get("columns", [])
            ],
            key=lambda x: x["name"],
        )

    raw = json.dumps(structural, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()[:32]
