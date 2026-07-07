"""
BusinessLens AI — Semantic Context Dataclass

SemanticContext is the resolved, ready-to-use business representation
of a connection's confirmed mapping. Every engine (Analytics, KPI, Dashboard,
AI Insight, Forecasting) consumes SemanticContext — never raw mappings.

This decouples all downstream engines from mapping implementation details.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID


@dataclass(frozen=True)
class SemanticColumn:
    """
    A resolved physical column with its business field binding.

    Immutable — the semantic layer is built once on mapping confirmation
    and invalidated atomically when the mapping changes.
    """
    table_name: str
    column_name: str
    physical_type: str
    business_field: str | None
    is_primary_key: bool = False
    is_foreign_key: bool = False
    references: str | None = None  # 'other_table.other_column'

    @property
    def full_name(self) -> str:
        """'table_name.column_name'"""
        return f"{self.table_name}.{self.column_name}"

    @property
    def qualified_sql_ref(self) -> str:
        """'"table_name"."column_name"' — safe for parameterized SQL templates."""
        return f'"{self.table_name}"."{self.column_name}"'


@dataclass
class SemanticJoinPath:
    """Describes a resolved FK join between two tables."""
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    relationship: str  # 'many-to-one' | 'one-to-many' | 'one-to-one'

    def to_sql_join_clause(self, join_type: str = "LEFT") -> str:
        """
        Generate a safe JOIN clause fragment.
        Returns: 'LEFT JOIN "to_table" ON "from_table"."from_col" = "to_table"."to_col"'
        """
        return (
            f'{join_type} JOIN "{self.to_table}" '
            f'ON "{self.from_table}"."{self.from_column}" '
            f'= "{self.to_table}"."{self.to_column}"'
        )


@dataclass
class SemanticContext:
    """
    Complete semantic business vocabulary for one confirmed connection mapping.

    This is the single source of truth consumed by all downstream engines.
    Built by SemanticLayer.build() on mapping confirmation or cache miss.

    Key capabilities:
    - resolve_field(business_field_name) → SemanticColumn
    - get_columns_for_table(table_name) → list[SemanticColumn]
    - find_join_path(from_table, to_table) → SemanticJoinPath | None
    - get_primary_table() → str
    """

    connection_id: UUID
    mapping_set_id: UUID
    organization_id: UUID

    # All resolved columns (both mapped and unmapped)
    columns: list[SemanticColumn] = field(default_factory=list)

    # Join paths derived from FK metadata + AI join hints
    join_paths: list[SemanticJoinPath] = field(default_factory=list)

    # Primary fact table (AI-suggested or user-confirmed)
    primary_table: str | None = None

    # Field-to-column lookup (built lazily in __post_init__)
    _field_index: dict[str, list[SemanticColumn]] = field(
        default_factory=dict, repr=False, compare=False
    )
    _table_index: dict[str, list[SemanticColumn]] = field(
        default_factory=dict, repr=False, compare=False
    )

    def __post_init__(self) -> None:
        self._rebuild_indexes()

    def _rebuild_indexes(self) -> None:
        """Build fast lookup indexes from the columns list."""
        field_idx: dict[str, list[SemanticColumn]] = {}
        table_idx: dict[str, list[SemanticColumn]] = {}
        for col in self.columns:
            if col.business_field:
                field_idx.setdefault(col.business_field, []).append(col)
            table_idx.setdefault(col.table_name, []).append(col)
        self._field_index = field_idx
        self._table_index = table_idx

    # ------------------------------------------------------------------ #
    # Resolution API
    # ------------------------------------------------------------------ #

    def resolve_field(self, business_field: str) -> SemanticColumn | None:
        """
        Resolve a business field name to its first matching SemanticColumn.
        Returns None if the field is not mapped in this context.
        """
        results = self._field_index.get(business_field, [])
        return results[0] if results else None

    def resolve_all(self, business_field: str) -> list[SemanticColumn]:
        """Return ALL columns mapped to a business field (e.g. Sales in multiple tables)."""
        return self._field_index.get(business_field, [])

    def get_columns_for_table(self, table_name: str) -> list[SemanticColumn]:
        """Return all columns for a specific table."""
        return self._table_index.get(table_name, [])

    def find_join_path(
        self, from_table: str, to_table: str
    ) -> SemanticJoinPath | None:
        """Find a direct join path between two tables."""
        for jp in self.join_paths:
            if jp.from_table == from_table and jp.to_table == to_table:
                return jp
            if jp.from_table == to_table and jp.to_table == from_table:
                # Return reversed path
                return SemanticJoinPath(
                    from_table=to_table,
                    from_column=jp.to_column,
                    to_table=from_table,
                    to_column=jp.from_column,
                    relationship=jp.relationship,
                )
        return None

    def get_primary_table(self) -> str | None:
        return self.primary_table

    def list_mapped_fields(self) -> list[str]:
        """Return all business field names that have at least one mapping."""
        return sorted(self._field_index.keys())

    def list_tables(self) -> list[str]:
        """Return all table names in this context."""
        return sorted(self._table_index.keys())

    def has_field(self, business_field: str) -> bool:
        return business_field in self._field_index

    def to_summary_dict(self) -> dict:
        """Lightweight summary for API responses."""
        return {
            "connection_id": str(self.connection_id),
            "mapping_set_id": str(self.mapping_set_id),
            "primary_table": self.primary_table,
            "tables": self.list_tables(),
            "mapped_fields": self.list_mapped_fields(),
            "join_paths": len(self.join_paths),
        }
