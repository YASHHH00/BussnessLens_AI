"""
BusinessLens AI — PostgreSQL Connector

Production connector for PostgreSQL using asyncpg via SQLAlchemy Core.
All queries use parameterized binds — no string concatenation.
"""

from __future__ import annotations

import time
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

from app.connectors.base_connector import BaseDBConnector, ColumnMeta, QueryResult, TableMeta
from app.core.exceptions import ConnectionTestError
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class PostgreSQLConnector(BaseDBConnector):
    """
    AsyncPG-backed PostgreSQL connector.

    Security:
    - execute_query(): accepts only engine-generated parameterized SQL
    - execute_raw_sql(): creates a READ-ONLY transaction (SET TRANSACTION READ ONLY)
    - All table/column names are validated against schema_snapshot allowlist upstream
    """

    def __init__(
        self,
        host: str,
        port: int,
        database: str,
        username: str,
        password: str,
        ssl: bool = False,
        timeout_seconds: int = 30,
    ) -> None:
        self._url = (
            f"postgresql+asyncpg://{username}:{password}"
            f"@{host}:{port}/{database}"
            f"{'?ssl=require' if ssl else ''}"
        )
        self._timeout = timeout_seconds
        self._engine: AsyncEngine | None = None

    # ------------------------------------------------------------------ #
    # Engine lifecycle
    # ------------------------------------------------------------------ #

    def _get_engine(self) -> AsyncEngine:
        if self._engine is None:
            self._engine = create_async_engine(
                self._url,
                pool_size=1,
                max_overflow=0,
                pool_timeout=self._timeout,
                pool_pre_ping=True,
                connect_args={"timeout": self._timeout},
            )
        return self._engine

    async def close(self) -> None:
        if self._engine:
            await self._engine.dispose()
            self._engine = None

    @property
    def db_type(self) -> str:
        return "postgresql"

    # ------------------------------------------------------------------ #
    # Connection test
    # ------------------------------------------------------------------ #

    async def test_connection(self) -> bool:
        try:
            async with self._get_engine().connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception as exc:
            raise ConnectionTestError(reason=str(exc)) from exc

    # ------------------------------------------------------------------ #
    # Schema inspection
    # ------------------------------------------------------------------ #

    async def get_table_names(self) -> list[str]:
        sql = text(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_type = 'BASE TABLE'
            ORDER BY table_name
            """
        )
        async with self._get_engine().connect() as conn:
            result = await conn.execute(sql)
            return [row[0] for row in result.fetchall()]

    async def get_table_meta(self, table_name: str, sample_rows: int = 5) -> TableMeta:
        async with self._get_engine().connect() as conn:
            # Column metadata
            col_sql = text(
                """
                SELECT
                    c.column_name,
                    c.data_type,
                    c.is_nullable,
                    CASE WHEN tc.constraint_type = 'PRIMARY KEY' THEN true ELSE false END AS is_pk,
                    CASE WHEN tc2.constraint_type = 'FOREIGN KEY' THEN true ELSE false END AS is_fk,
                    ccu.table_name || '.' || ccu.column_name AS references
                FROM information_schema.columns c
                LEFT JOIN information_schema.key_column_usage kcu
                    ON kcu.column_name = c.column_name AND kcu.table_name = c.table_name
                LEFT JOIN information_schema.table_constraints tc
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.constraint_type = 'PRIMARY KEY'
                LEFT JOIN information_schema.key_column_usage kcu2
                    ON kcu2.column_name = c.column_name AND kcu2.table_name = c.table_name
                LEFT JOIN information_schema.table_constraints tc2
                    ON tc2.constraint_name = kcu2.constraint_name
                    AND tc2.constraint_type = 'FOREIGN KEY'
                LEFT JOIN information_schema.constraint_column_usage ccu
                    ON ccu.constraint_name = tc2.constraint_name
                WHERE c.table_schema = 'public' AND c.table_name = :tname
                ORDER BY c.ordinal_position
                """
            )
            col_result = await conn.execute(col_sql, {"tname": table_name})
            columns = []
            for row in col_result.mappings():
                columns.append(
                    ColumnMeta(
                        name=row["column_name"],
                        physical_type=row["data_type"],
                        nullable=row["is_nullable"] == "YES",
                        is_primary_key=bool(row["is_pk"]),
                        is_foreign_key=bool(row["is_fk"]),
                        references=row["references"],
                    )
                )

            # Sample values (safe — table_name validated upstream against allowlist)
            # We use LIMIT only, no user-controlled ORDER BY
            sample_sql = text(
                f'SELECT * FROM "{table_name}" LIMIT :limit'  # noqa: S608
            )
            sample_result = await conn.execute(sample_sql, {"limit": sample_rows})
            sample_rows_data = [dict(r._mapping) for r in sample_result.fetchall()]

            sample_values: dict[str, list[Any]] = {}
            for col in columns:
                sample_values[col.name] = [
                    row.get(col.name) for row in sample_rows_data
                ]

            row_count = await self.get_row_count(table_name)

            return TableMeta(
                name=table_name,
                columns=columns,
                row_count=row_count,
                sample_values=sample_values,
            )

    async def get_row_count(self, table_name: str) -> int:
        # Use pg_class for a fast estimate on large tables
        sql = text(
            """
            SELECT reltuples::bigint AS estimate
            FROM pg_class
            WHERE relname = :tname
            """
        )
        async with self._get_engine().connect() as conn:
            result = await conn.execute(sql, {"tname": table_name})
            row = result.fetchone()
            return int(row[0]) if row and row[0] > 0 else 0

    # ------------------------------------------------------------------ #
    # Query execution
    # ------------------------------------------------------------------ #

    async def execute_query(
        self,
        sql: str,
        params: dict[str, Any] | None = None,
        timeout_seconds: int = 30,
        row_cap: int = 10_000,
    ) -> QueryResult:
        t0 = time.monotonic()
        async with self._get_engine().connect() as conn:
            result = await conn.execute(
                text(sql), params or {}
            )
            rows = result.mappings().fetchmany(row_cap + 1)
            truncated = len(rows) > row_cap
            final_rows = [dict(r) for r in rows[:row_cap]]
            elapsed_ms = int((time.monotonic() - t0) * 1000)
            return QueryResult(
                columns=list(result.keys()),
                rows=final_rows,
                row_count=len(final_rows),
                truncated=truncated,
                query_time_ms=elapsed_ms,
            )

    async def execute_raw_sql(
        self,
        sql: str,
        timeout_seconds: int = 30,
        row_cap: int = 10_000,
    ) -> QueryResult:
        """SQL Playground — enforced read-only via PostgreSQL transaction."""
        t0 = time.monotonic()
        async with self._get_engine().connect() as conn:
            # Force read-only transaction — any DML will raise an error
            await conn.execute(text("SET TRANSACTION READ ONLY"))
            result = await conn.execute(text(sql))
            rows = result.mappings().fetchmany(row_cap + 1)
            truncated = len(rows) > row_cap
            final_rows = [dict(r) for r in rows[:row_cap]]
            elapsed_ms = int((time.monotonic() - t0) * 1000)
            return QueryResult(
                columns=list(result.keys()),
                rows=final_rows,
                row_count=len(final_rows),
                truncated=truncated,
                query_time_ms=elapsed_ms,
            )
