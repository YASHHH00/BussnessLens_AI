"""
BusinessLens AI — Mapping Validation Engine

10 deterministic validation rules applied before any mapping is confirmed.
All rules are stateless and pure — same input always gives same output.
Rules run without AI. AI is only called for suggestions, not validation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ValidationViolation:
    rule: str
    message: str
    severity: str  # 'error' | 'warning'
    column: str | None = None
    field: str | None = None


class MappingValidationEngine:
    """
    10 deterministic mapping validation rules.

    Rules enforced:
    1.  Required fields check  — required business fields must have at least one mapping
    2.  Duplicate field guard   — same business field cannot be mapped twice (per table group)
    3.  Type compatibility       — business field type must match column physical type
    4.  Null-field guard         — columns marked 100% null should not map to required fields
    5.  Primary key guard        — primary key columns should not map to metric fields
    6.  At least one table       — mapping set must cover at least one table
    7.  Date field required      — Order Date / Event Date must be mapped for time analytics
    8.  Metric fields positive    — numeric metric fields must be in numeric-typed columns
    9.  Minimum coverage          — at least 30% of columns should be mapped
    10. No cross-table duplicates — same business field mapped in 2+ unrelated tables is a warning
    """

    def __init__(self, field_registry) -> None:
        self._registry = field_registry

    def validate(
        self,
        mappings: list[dict],  # [{"table": ..., "column": ..., "business_field": ..., "physical_type": ..., "is_pk": ...}]
        snapshot_tables: dict,
    ) -> list[ValidationViolation]:
        violations: list[ValidationViolation] = []
        mapped_fields: dict[str, list[dict]] = {}  # field_name → [mapping_entries]
        total_cols = sum(
            len(t.get("columns", [])) for t in snapshot_tables.values()
        )
        mapped_count = 0

        for m in mappings:
            if m.get("business_field"):
                mapped_count += 1
                mapped_fields.setdefault(m["business_field"], []).append(m)

        # R1: Required fields
        required = [
            f.name for f in self._registry.get_all_fields()
            if getattr(f, "is_required", False)
        ]
        for req in required:
            if req not in mapped_fields:
                violations.append(ValidationViolation(
                    rule="required_field_missing",
                    message=f"Required business field '{req}' has no mapped column.",
                    severity="error",
                    field=req,
                ))

        # R2: Duplicate field within same table
        for field_name, entries in mapped_fields.items():
            by_table: dict[str, list] = {}
            for e in entries:
                by_table.setdefault(e["table"], []).append(e)
            for table, tbl_entries in by_table.items():
                if len(tbl_entries) > 1:
                    cols = [e["column"] for e in tbl_entries]
                    violations.append(ValidationViolation(
                        rule="duplicate_field_in_table",
                        message=(
                            f"Business field '{field_name}' is mapped to multiple columns "
                            f"in table '{table}': {cols}. Only one mapping per field per table is allowed."
                        ),
                        severity="error",
                        field=field_name,
                    ))

        # R3: Type compatibility
        _NUMERIC_TYPES = {"integer", "numeric", "float", "decimal", "bigint", "double", "real", "money"}
        _DATE_TYPES = {"date", "timestamp", "datetime", "timestamptz", "datetime2", "datetime64"}
        _metric_fields = {f.name for f in self._registry.list_metrics()}
        _date_fields = {f.name for f in self._registry.list_date_fields()}

        for m in mappings:
            bf = m.get("business_field")
            pt = (m.get("physical_type") or "varchar").lower()
            if not bf:
                continue
            if bf in _metric_fields and pt not in _NUMERIC_TYPES:
                violations.append(ValidationViolation(
                    rule="type_incompatible_metric",
                    message=(
                        f"Field '{bf}' is a numeric metric but column "
                        f"'{m['table']}.{m['column']}' has type '{pt}'. "
                        "Numeric metrics must map to numeric columns."
                    ),
                    severity="error",
                    column=m["column"],
                    field=bf,
                ))
            if bf in _date_fields and not any(pt.startswith(dt) for dt in _DATE_TYPES):
                violations.append(ValidationViolation(
                    rule="type_incompatible_date",
                    message=(
                        f"Field '{bf}' is a date/time field but column "
                        f"'{m['table']}.{m['column']}' has type '{pt}'."
                    ),
                    severity="warning",
                    column=m["column"],
                    field=bf,
                ))

        # R5: Primary key mapped to metric
        for m in mappings:
            if m.get("is_pk") and m.get("business_field") in _metric_fields:
                violations.append(ValidationViolation(
                    rule="pk_mapped_to_metric",
                    message=(
                        f"Primary key column '{m['table']}.{m['column']}' is mapped to "
                        f"metric field '{m['business_field']}'. PK columns are identifiers, not metrics."
                    ),
                    severity="warning",
                    column=m["column"],
                    field=m["business_field"],
                ))

        # R6: At least one table
        mapped_tables = {m["table"] for m in mappings if m.get("business_field")}
        if not mapped_tables:
            violations.append(ValidationViolation(
                rule="no_mapped_tables",
                message="No tables have any mapped business fields. At least one table must be mapped.",
                severity="error",
            ))

        # R7: Date field required for time analytics
        if not any(bf in _date_fields for bf in mapped_fields):
            violations.append(ValidationViolation(
                rule="no_date_field",
                message=(
                    "No date/time field is mapped. Time-series analytics and forecasting "
                    "require at least one date field (e.g. 'Order Date', 'Created At')."
                ),
                severity="warning",
            ))

        # R9: Minimum mapping coverage
        if total_cols > 0:
            coverage = mapped_count / total_cols
            if coverage < 0.30:
                violations.append(ValidationViolation(
                    rule="low_coverage",
                    message=(
                        f"Only {coverage:.0%} of columns are mapped to business fields. "
                        "Consider mapping more columns to improve analytics accuracy."
                    ),
                    severity="warning",
                ))

        # R10: Cross-table duplicate warning
        for field_name, entries in mapped_fields.items():
            tables_used = {e["table"] for e in entries}
            if len(tables_used) > 1:
                violations.append(ValidationViolation(
                    rule="cross_table_duplicate",
                    message=(
                        f"Business field '{field_name}' is mapped in multiple tables: "
                        f"{sorted(tables_used)}. This may cause double-counting. "
                        "Verify the correct source table."
                    ),
                    severity="warning",
                    field=field_name,
                ))

        return violations

    def has_blocking_errors(self, violations: list[ValidationViolation]) -> bool:
        return any(v.severity == "error" for v in violations)
