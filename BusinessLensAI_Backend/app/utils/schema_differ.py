"""
BusinessLens AI — Schema Differ

Detects schema changes between two snapshots.
Produces a structured diff used to invalidate mappings and notify users.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ColumnChange:
    table: str
    column: str
    change_type: str   # 'added', 'removed', 'type_changed', 'nullable_changed'
    old_value: str | None = None
    new_value: str | None = None


@dataclass
class SchemaDiff:
    tables_added: list[str] = field(default_factory=list)
    tables_removed: list[str] = field(default_factory=list)
    column_changes: list[ColumnChange] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.tables_added or self.tables_removed or self.column_changes)

    @property
    def is_breaking(self) -> bool:
        """Returns True if any change would invalidate existing mappings."""
        for change in self.column_changes:
            if change.change_type in ("removed", "type_changed"):
                return True
        return bool(self.tables_removed)

    def to_dict(self) -> dict:
        return {
            "tables_added": self.tables_added,
            "tables_removed": self.tables_removed,
            "column_changes": [
                {
                    "table": c.table,
                    "column": c.column,
                    "change_type": c.change_type,
                    "old_value": c.old_value,
                    "new_value": c.new_value,
                }
                for c in self.column_changes
            ],
            "has_changes": self.has_changes,
            "is_breaking": self.is_breaking,
        }


def compute_schema_diff(
    old_tables: dict,
    new_tables: dict,
) -> SchemaDiff:
    """
    Compare two tables_json dicts and return a SchemaDiff.

    old_tables / new_tables format:
    {
        "table_name": {
            "columns": [{"name": ..., "physical_type": ..., "nullable": ...}, ...]
        }
    }
    """
    diff = SchemaDiff()

    old_names = set(old_tables.keys())
    new_names = set(new_tables.keys())

    diff.tables_added = sorted(new_names - old_names)
    diff.tables_removed = sorted(old_names - new_names)

    # Check columns in common tables
    for table_name in old_names & new_names:
        old_cols = {c["name"]: c for c in old_tables[table_name].get("columns", [])}
        new_cols = {c["name"]: c for c in new_tables[table_name].get("columns", [])}

        for col_name in set(old_cols) - set(new_cols):
            diff.column_changes.append(
                ColumnChange(table=table_name, column=col_name, change_type="removed")
            )
        for col_name in set(new_cols) - set(old_cols):
            diff.column_changes.append(
                ColumnChange(table=table_name, column=col_name, change_type="added")
            )
        for col_name in set(old_cols) & set(new_cols):
            o, n = old_cols[col_name], new_cols[col_name]
            if o.get("physical_type") != n.get("physical_type"):
                diff.column_changes.append(
                    ColumnChange(
                        table=table_name, column=col_name,
                        change_type="type_changed",
                        old_value=o.get("physical_type"),
                        new_value=n.get("physical_type"),
                    )
                )
            elif o.get("nullable") != n.get("nullable"):
                diff.column_changes.append(
                    ColumnChange(
                        table=table_name, column=col_name,
                        change_type="nullable_changed",
                        old_value=str(o.get("nullable")),
                        new_value=str(n.get("nullable")),
                    )
                )

    return diff
