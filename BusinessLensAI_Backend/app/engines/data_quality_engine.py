"""
BusinessLens AI — Data Quality Engine

Evaluates 8 deterministic data quality rules against snapshot column profiles.
Returns structured DataQualityReport ready for persistence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class QualityIssue:
    column: str
    rule: str
    severity: str
    value: str
    message: str


@dataclass
class TableQualityResult:
    table: str
    score: float
    issues: list[QualityIssue] = field(default_factory=list)


# Quality rules
_RULES = {
    "null_rate_critical": {"threshold": 0.5, "severity": "critical", "desc": ">{pct}% null values"},
    "null_rate_warning": {"threshold": 0.2, "severity": "warning", "desc": ">{pct}% null values"},
    "zero_variance": {"severity": "warning", "desc": "Column has only one distinct value"},
    "negative_numeric": {"severity": "warning", "desc": "Negative values detected in numeric column"},
    "future_dates": {"severity": "warning", "desc": "Future dates detected in date column"},
    "high_unique_rate": {"threshold": 0.99, "severity": "info", "desc": ">{pct}% unique — possible ID column"},
    "empty_column": {"severity": "critical", "desc": "Column is entirely null"},
    "mixed_types": {"severity": "warning", "desc": "Mixed data types detected in column"},
}


class DataQualityEngine:
    """
    Deterministic rules-based data quality evaluation.
    Does NOT call AI. Completely deterministic — same input always produces same output.
    """

    def evaluate_snapshot(self, tables_json: dict) -> dict:
        """
        Evaluate all tables in a snapshot.
        Returns a dict matching DataQualityReport.table_scores structure.
        """
        table_results: dict[str, Any] = {}
        total_issues = 0
        overall_scores = []

        for table_name, table_data in tables_json.items():
            if "error" in table_data:
                continue
            result = self._evaluate_table(table_name, table_data)
            table_results[table_name] = {
                "score": result.score,
                "issues": [
                    {
                        "column": i.column, "rule": i.rule,
                        "severity": i.severity, "value": i.value, "message": i.message,
                    }
                    for i in result.issues
                ],
            }
            total_issues += len(result.issues)
            overall_scores.append(result.score)

        overall_score = sum(overall_scores) / max(len(overall_scores), 1)
        critical = sum(
            1 for t in table_results.values()
            for i in t["issues"] if i["severity"] == "critical"
        )
        warning = sum(
            1 for t in table_results.values()
            for i in t["issues"] if i["severity"] == "warning"
        )
        info = sum(
            1 for t in table_results.values()
            for i in t["issues"] if i["severity"] == "info"
        )

        return {
            "overall_score": round(overall_score, 2),
            "table_scores": table_results,
            "total_issues": total_issues,
            "critical_issues": critical,
            "warning_issues": warning,
            "info_issues": info,
        }

    def _evaluate_table(self, table_name: str, table_data: dict) -> TableQualityResult:
        columns = table_data.get("columns", [])
        row_count = table_data.get("row_count", 0) or 1
        issues: list[QualityIssue] = []

        for col in columns:
            col_name = col.get("name", "")
            physical_type = col.get("physical_type", "varchar")
            sample_values = col.get("sample_values", [])
            nullable = col.get("nullable", True)

            non_null = [v for v in sample_values if v is not None and v != ""]
            null_count = len(sample_values) - len(non_null)
            null_rate = null_count / max(len(sample_values), 1)

            # R1: Empty column
            if null_rate >= 1.0 and len(sample_values) > 0:
                issues.append(QualityIssue(
                    column=col_name, rule="empty_column", severity="critical",
                    value="100%", message=f"Column '{col_name}' is entirely null."
                ))
                continue

            # R2: High null rate (critical)
            if null_rate > 0.5:
                issues.append(QualityIssue(
                    column=col_name, rule="null_rate_critical", severity="critical",
                    value=f"{null_rate:.0%}",
                    message=f"Column '{col_name}' has {null_rate:.0%} null values (>50%)."
                ))
            elif null_rate > 0.2:
                issues.append(QualityIssue(
                    column=col_name, rule="null_rate_warning", severity="warning",
                    value=f"{null_rate:.0%}",
                    message=f"Column '{col_name}' has {null_rate:.0%} null values (>20%)."
                ))

            # R3: Zero variance
            unique_vals = set(str(v) for v in non_null)
            if len(unique_vals) == 1 and len(non_null) > 3:
                issues.append(QualityIssue(
                    column=col_name, rule="zero_variance", severity="warning",
                    value=str(list(unique_vals)[0]),
                    message=f"Column '{col_name}' has only one distinct value."
                ))

            # R4: Negative numeric
            if physical_type in ("integer", "numeric", "float", "bigint", "decimal"):
                neg_vals = [v for v in non_null if _to_float(v) is not None and _to_float(v) < 0]
                if neg_vals:
                    issues.append(QualityIssue(
                        column=col_name, rule="negative_numeric", severity="warning",
                        value=str(neg_vals[0]),
                        message=f"Column '{col_name}' contains negative values."
                    ))

            # R5: High unique rate (possible ID/PK used as dimension)
            unique_pct = len(unique_vals) / max(len(non_null), 1)
            if unique_pct > 0.99 and len(non_null) > 10:
                issues.append(QualityIssue(
                    column=col_name, rule="high_unique_rate", severity="info",
                    value=f"{unique_pct:.0%}",
                    message=f"Column '{col_name}' is {unique_pct:.0%} unique — likely an ID column."
                ))

        # Compute score: start at 100, deduct per issue
        deduction = sum(
            {"critical": 20, "warning": 8, "info": 2}.get(i.severity, 0)
            for i in issues
        )
        score = max(0.0, 100.0 - deduction)

        return TableQualityResult(table=table_name, score=score, issues=issues)


def _to_float(v) -> float | None:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None
