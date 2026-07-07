"""
BusinessLens AI — Base DB Connector Abstract Class

Every database connector implements this interface.
The Analytics Engine, Schema Detection, and SQL Playground
use this abstraction — they never know which specific DB they're talking to.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ColumnMeta:
    """Metadata for a single column returned by schema inspection."""
    name: str
    physical_type: str       # 'varchar', 'integer', 'timestamp', etc.
    nullable: bool
    is_primary_key: bool
    is_foreign_key: bool
    references: str | None   # 'other_table.column' if foreign key


@dataclass
class TableMeta:
    """Metadata for a single table returned by schema inspection."""
    name: str
    columns: list[ColumnMeta]
    row_count: int | None    # None if counting was skipped (large tables)
    sample_values: dict[str, list[Any]]  # {column_name: [val1, val2, ...]}


@dataclass
class QueryResult:
    """Result of an executed SQL query."""
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int
    truncated: bool          # True if rows were capped at QUERY_ROW_CAP
    query_time_ms: int


class BaseDBConnector(ABC):
    """
    Abstract connector — all DB/file source adapters implement this.

    Lifecycle:
    1. Created by ConnectorFactory with decrypted credentials.
    2. `test_connection()` called to validate the credentials.
    3. `get_tables()` and `get_table_meta()` used by SchemaDetectionService.
    4. `execute_query()` used by AnalyticsEngine (read-only, metadata-driven).
    5. `execute_raw_sql()` used ONLY by SqlPlaygroundService (Data Analyst + Admin role).
    6. `close()` called after each operation (no persistent connections per request).

    Security:
    - `execute_query()` MUST only accept allow-listed, engine-constructed SQL.
    - `execute_raw_sql()` is restricted to SQL Playground — role guard is in the service layer.
    - SSRF guard must be applied at the service layer before calling the connector factory.
    """

    @abstractmethod
    async def test_connection(self) -> bool:
        """
        Verify credentials and connectivity.
        Returns True on success.
        Raises ConnectionTestError with a descriptive reason on failure.
        """
        ...

    @abstractmethod
    async def get_table_names(self) -> list[str]:
        """Return all user-visible table names in the connected database/schema."""
        ...

    @abstractmethod
    async def get_table_meta(
        self, table_name: str, sample_rows: int = 5
    ) -> TableMeta:
        """
        Inspect a single table — returns column metadata and sample values.
        sample_rows: number of sample values to collect per column (max 5).
        """
        ...

    @abstractmethod
    async def get_row_count(self, table_name: str) -> int:
        """Return an estimated or exact row count for a table."""
        ...

    @abstractmethod
    async def execute_query(
        self,
        sql: str,
        params: dict[str, Any] | None = None,
        timeout_seconds: int = 30,
        row_cap: int = 10_000,
    ) -> QueryResult:
        """
        Execute a parameterized, engine-generated SQL statement.
        Parameters use named binds (`:param_name` style) to prevent injection.
        Results are capped at `row_cap` rows.
        """
        ...

    @abstractmethod
    async def execute_raw_sql(
        self,
        sql: str,
        timeout_seconds: int = 30,
        row_cap: int = 10_000,
    ) -> QueryResult:
        """
        Execute raw SQL (SQL Playground only).
        Service layer MUST enforce: role in (DATA_ANALYST, ADMIN).
        Connection MUST be read-only (enforced by connector implementation).
        """
        ...

    @abstractmethod
    async def close(self) -> None:
        """Release the connection back to the pool or close it."""
        ...

    @property
    @abstractmethod
    def db_type(self) -> str:
        """The database type identifier. e.g. 'postgresql', 'mysql'"""
        ...

    async def __aenter__(self) -> "BaseDBConnector":
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()
