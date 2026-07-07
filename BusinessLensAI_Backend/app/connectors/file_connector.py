"""
BusinessLens AI — CSV / Excel File Connector

Wraps pandas DataFrames to expose the same BaseDBConnector interface
as database connectors. Enables file uploads to work seamlessly with
the Schema Detection, Mapping, and Analytics pipelines.
"""

from __future__ import annotations

import time
from typing import Any

import pandas as pd

from app.connectors.base_connector import BaseDBConnector, ColumnMeta, QueryResult, TableMeta
from app.core.exceptions import ConnectionTestError
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Map pandas dtypes to canonical physical type strings
_DTYPE_MAP: dict[str, str] = {
    "int64": "integer",
    "int32": "integer",
    "float64": "numeric",
    "float32": "numeric",
    "object": "varchar",
    "bool": "boolean",
    "datetime64[ns]": "timestamp",
    "datetime64[us]": "timestamp",
}


def _pandas_type_to_physical(dtype_name: str) -> str:
    for key, val in _DTYPE_MAP.items():
        if dtype_name.startswith(key):
            return val
    return "varchar"


class FileConnector(BaseDBConnector):
    """
    Connector for CSV and Excel files.
    Loads the file into an in-memory pandas DataFrame.
    The 'table name' is always the sanitized filename stem.
    """

    def __init__(self, file_path: str, connection_type: str = "csv") -> None:
        self._file_path = file_path
        self._connection_type = connection_type
        self._df: pd.DataFrame | None = None
        self._table_name: str = ""

    # ------------------------------------------------------------------ #
    # Load data
    # ------------------------------------------------------------------ #

    def _load(self) -> pd.DataFrame:
        if self._df is None:
            import os
            self._table_name = os.path.splitext(os.path.basename(self._file_path))[0]
            if self._connection_type == "csv":
                self._df = pd.read_csv(self._file_path, nrows=50_000)
            elif self._connection_type == "excel":
                self._df = pd.read_excel(self._file_path, nrows=50_000)
            else:
                raise ValueError(f"Unsupported file type: {self._connection_type}")
        return self._df

    # ------------------------------------------------------------------ #
    # BaseDBConnector interface
    # ------------------------------------------------------------------ #

    @property
    def db_type(self) -> str:
        return self._connection_type

    async def test_connection(self) -> bool:
        try:
            self._load()
            return True
        except Exception as exc:
            raise ConnectionTestError(reason=str(exc)) from exc

    async def get_table_names(self) -> list[str]:
        df = self._load()
        return [self._table_name]

    async def get_table_meta(self, table_name: str, sample_rows: int = 5) -> TableMeta:
        df = self._load()
        columns: list[ColumnMeta] = []
        sample_values: dict[str, list[Any]] = {}

        for col_name in df.columns:
            dtype_str = str(df[col_name].dtype)
            null_count = int(df[col_name].isna().sum())
            columns.append(
                ColumnMeta(
                    name=col_name,
                    physical_type=_pandas_type_to_physical(dtype_str),
                    nullable=null_count > 0,
                    is_primary_key=False,
                    is_foreign_key=False,
                    references=None,
                )
            )
            # Collect non-null sample values
            non_null = df[col_name].dropna().head(sample_rows)
            sample_values[col_name] = [str(v) for v in non_null.tolist()]

        return TableMeta(
            name=table_name,
            columns=columns,
            row_count=len(df),
            sample_values=sample_values,
        )

    async def get_row_count(self, table_name: str) -> int:
        df = self._load()
        return len(df)

    async def execute_query(
        self,
        sql: str,
        params: dict[str, Any] | None = None,
        timeout_seconds: int = 30,
        row_cap: int = 10_000,
    ) -> QueryResult:
        """
        Execute a simple SQL query against the in-memory DataFrame using pandasql.
        Limited to SELECT operations.
        """
        t0 = time.monotonic()
        try:
            import pandasql as ps  # type: ignore[import]
        except ImportError:
            # Fallback: return full DataFrame if pandasql not available
            df = self._load().head(row_cap)
            rows = df.to_dict("records")
            elapsed_ms = int((time.monotonic() - t0) * 1000)
            return QueryResult(
                columns=list(df.columns),
                rows=rows,
                row_count=len(rows),
                truncated=len(self._load()) > row_cap,
                query_time_ms=elapsed_ms,
            )

        df = self._load()
        env = {self._table_name: df}
        result_df = ps.sqldf(sql, env)
        rows = result_df.head(row_cap).to_dict("records")
        elapsed_ms = int((time.monotonic() - t0) * 1000)
        return QueryResult(
            columns=list(result_df.columns),
            rows=rows,
            row_count=len(rows),
            truncated=len(result_df) > row_cap,
            query_time_ms=elapsed_ms,
        )

    async def execute_raw_sql(
        self,
        sql: str,
        timeout_seconds: int = 30,
        row_cap: int = 10_000,
    ) -> QueryResult:
        return await self.execute_query(sql, row_cap=row_cap)

    async def close(self) -> None:
        self._df = None
