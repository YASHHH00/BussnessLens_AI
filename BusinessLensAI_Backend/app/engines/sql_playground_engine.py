"""
BusinessLens AI — SQL Playground Engine

Role-gated read-only query execution engine for Data Analysts and Admins.
Enforces strict statement validation to block write/DDL queries and injects row limits.
"""

from __future__ import annotations

import re
import time
from typing import Any

from app.connectors.base_connector import BaseDBConnector
from app.core.exceptions import ValidationError
from app.core.logging_config import get_logger
from app.schemas.sql_playground import SQLPlaygroundResponse

logger = get_logger(__name__)

_FORBIDDEN_REGEX = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|GRANT|REVOKE|EXEC|EXECUTE|MERGE|CALL)\b",
    re.IGNORECASE,
)


class SQLPlaygroundEngine:
    async def execute_readonly(
        self,
        connector: BaseDBConnector,
        query: str,
        max_rows: int = 1000,
    ) -> SQLPlaygroundResponse:
        clean_query = query.strip()
        if not clean_query:
            raise ValidationError("Query cannot be empty.")

        # Strip trailing semicolons
        clean_query = clean_query.rstrip(";")

        # Check for forbidden keywords
        if _FORBIDDEN_REGEX.search(clean_query):
            raise ValidationError("Only read-only SELECT or EXPLAIN queries are permitted.")

        # Ensure query starts with SELECT or EXPLAIN or WITH
        first_word = clean_query.split()[0].upper()
        if first_word not in ("SELECT", "EXPLAIN", "WITH"):
            raise ValidationError("Query must begin with SELECT, WITH, or EXPLAIN.")

        # Check if LIMIT already present; if not or if > max_rows, wrap or append
        if "LIMIT " not in clean_query.upper():
            clean_query = f"{clean_query}\nLIMIT {max_rows}"

        t0 = time.monotonic()
        async with connector:
            rows = await connector.execute_query(clean_query, {})

        elapsed = int((time.monotonic() - t0) * 1000)
        columns = list(rows[0].keys()) if rows else []

        return SQLPlaygroundResponse(
            query_executed=clean_query,
            columns=columns,
            rows=rows[:max_rows],
            total_rows=len(rows[:max_rows]),
            execution_time_ms=elapsed,
        )
