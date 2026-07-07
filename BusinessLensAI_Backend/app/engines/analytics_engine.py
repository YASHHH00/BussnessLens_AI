"""
BusinessLens AI — Analytics Engine

Dynamic SQL construction engine that translates business queries into dialect-safe SQL.
Strictly consumes SemanticContext and BusinessFieldRegistry.
Enforces parameterized execution, identifier quoting, and join resolution.
"""

from __future__ import annotations

import time
from typing import Any

from app.connectors.base_connector import BaseDBConnector
from app.core.exceptions import ValidationError
from app.core.logging_config import get_logger
from app.registry.field_registry import BusinessFieldRegistry
from app.schemas.analytics import AnalyticsQueryRequest, AnalyticsQueryResult, FilterCondition
from app.semantic.semantic_context import SemanticColumn, SemanticContext

logger = get_logger(__name__)


class AnalyticsEngine:
    """
    Translates semantic vocabulary queries into SQL and executes via connector.
    Never exposes or accepts raw physical SQL from users.
    """

    def __init__(self, registry: BusinessFieldRegistry) -> None:
        self._registry = registry

    async def execute_query(
        self,
        connector: BaseDBConnector,
        context: SemanticContext,
        request: AnalyticsQueryRequest,
        include_debug_sql: bool = False,
    ) -> AnalyticsQueryResult:
        """
        Build and execute a semantic query.
        """
        t0 = time.monotonic()
        sql, params = self.build_sql(context, request)

        logger.debug("Executing semantic query: %s | params=%s", sql, params)
        async with connector:
            rows = await connector.execute_query(sql, params)

        elapsed_ms = int((time.monotonic() - t0) * 1000)
        columns = list(rows[0].keys()) if rows else []

        return AnalyticsQueryResult(
            columns=columns,
            rows=rows,
            total_rows=len(rows),
            execution_time_ms=elapsed_ms,
            sql_executed=sql if include_debug_sql else None,
        )

    def build_sql(
        self,
        context: SemanticContext,
        request: AnalyticsQueryRequest,
    ) -> tuple[str, dict[str, Any]]:
        """
        Build parameterized SQL from AnalyticsQueryRequest and SemanticContext.
        Returns (sql_string, params_dict).
        """
        # 1. Resolve all requested fields to SemanticColumn objects
        select_clauses: list[str] = []
        group_by_clauses: list[str] = []
        tables_needed: set[str] = set()
        params: dict[str, Any] = {}
        param_idx = 1

        # Resolve dimensions
        for dim_field in request.dimensions:
            sem_col = self._resolve_field_or_raise(context, dim_field)
            tables_needed.add(sem_col.table_name)
            expr = sem_col.qualified_sql_ref
            alias = self._quote_ident(dim_field)
            select_clauses.append(f"{expr} AS {alias}")
            group_by_clauses.append(expr)

        # Resolve time grain if temporal field requested
        if request.date_range_field and request.time_grain:
            sem_col = self._resolve_field_or_raise(context, request.date_range_field)
            tables_needed.add(sem_col.table_name)
            grain_expr = self._format_time_grain(sem_col.qualified_sql_ref, request.time_grain)
            grain_alias = self._quote_ident(f"{request.date_range_field} ({request.time_grain})")
            select_clauses.append(f"{grain_expr} AS {grain_alias}")
            group_by_clauses.append(grain_expr)

        # Resolve metrics
        for metric_field in request.metrics:
            sem_col = self._resolve_field_or_raise(context, metric_field)
            tables_needed.add(sem_col.table_name)
            agg = self._registry.get_default_aggregation(metric_field).upper()
            expr = f"{agg}({sem_col.qualified_sql_ref})"
            alias = self._quote_ident(metric_field)
            select_clauses.append(f"{expr} AS {alias}")

        if not select_clauses:
            raise ValidationError("Query must specify at least one metric or dimension.")

        # 2. Determine base table and JOINs
        base_table = context.primary_table
        if not base_table or base_table not in context.list_tables():
            base_table = sorted(tables_needed)[0] if tables_needed else "unknown"
        tables_needed.add(base_table)

        from_clause = f'"{base_table}"'
        joined_tables = {base_table}

        for target_table in sorted(tables_needed - joined_tables):
            join_path = context.find_join_path(base_table, target_table)
            if join_path:
                from_clause += " " + join_path.to_sql_join_clause("LEFT")
                joined_tables.add(target_table)
            else:
                # Try joining to any already joined table
                joined = False
                for existing in list(joined_tables):
                    jp = context.find_join_path(existing, target_table)
                    if jp:
                        from_clause += " " + jp.to_sql_join_clause("LEFT")
                        joined_tables.add(target_table)
                        joined = True
                        break
                if not joined:
                    # Fallback cross join or implicit warning
                    logger.warning("No explicit join path found between %s and %s", base_table, target_table)
                    from_clause += f', "{target_table}"'
                    joined_tables.add(target_table)

        # 3. Build WHERE clauses
        where_conditions: list[str] = []

        if request.date_range_field and (request.start_date or request.end_date):
            sem_col = self._resolve_field_or_raise(context, request.date_range_field)
            tables_needed.add(sem_col.table_name)
            if request.start_date:
                p_name = f"p_{param_idx}"
                param_idx += 1
                where_conditions.append(f"{sem_col.qualified_sql_ref} >= :{p_name}")
                params[p_name] = request.start_date
            if request.end_date:
                p_name = f"p_{param_idx}"
                param_idx += 1
                where_conditions.append(f"{sem_col.qualified_sql_ref} <= :{p_name}")
                params[p_name] = request.end_date

        for flt in request.filters:
            sem_col = self._resolve_field_or_raise(context, flt.field)
            tables_needed.add(sem_col.table_name)
            cond_sql, p_dict = self._format_filter(sem_col, flt, param_idx)
            where_conditions.append(cond_sql)
            params.update(p_dict)
            param_idx += len(p_dict)

        # Assemble query
        sql = f"SELECT {', '.join(select_clauses)}\nFROM {from_clause}"
        if where_conditions:
            sql += f"\nWHERE {' AND '.join(where_conditions)}"
        if group_by_clauses:
            sql += f"\nGROUP BY {', '.join(group_by_clauses)}"

        # ORDER BY
        if request.order_by:
            if request.order_by in request.metrics or request.order_by in request.dimensions:
                order_expr = self._quote_ident(request.order_by)
            else:
                sem_col = context.resolve_field(request.order_by)
                order_expr = sem_col.qualified_sql_ref if sem_col else self._quote_ident(request.order_by)
            direction = "ASC" if request.order_direction.lower() == "asc" else "DESC"
            sql += f"\nORDER BY {order_expr} {direction}"

        # LIMIT
        sql += f"\nLIMIT {int(request.limit)}"

        return sql, params

    def _resolve_field_or_raise(self, context: SemanticContext, field_name: str) -> SemanticColumn:
        col = context.resolve_field(field_name)
        if not col:
            raise ValidationError(f"Requested business field '{field_name}' is not mapped in this connection schema.")
        return col

    def _quote_ident(self, ident: str, dialect: str = "postgres") -> str:
        if dialect.lower() in ("mysql", "mariadb"):
            clean = ident.replace("`", "``")
            return f"`{clean}`"
        clean = ident.replace('"', '""')
        return f'"{clean}"'

    def _format_time_grain(self, col_ref: str, grain: str) -> str:
        grain_lower = grain.lower()
        if grain_lower in ("day", "month", "year", "quarter", "week"):
            return f"DATE_TRUNC('{grain_lower}', {col_ref}::timestamp)"
        return col_ref

    def _format_filter(
        self,
        col: SemanticColumn,
        flt: FilterCondition,
        start_idx: int,
    ) -> tuple[str, dict[str, Any]]:
        ref = col.qualified_sql_ref
        op = flt.operator.lower()
        val = flt.value

        p_name = f"p_{start_idx}"
        if op == "eq":
            return f"{ref} = :{p_name}", {p_name: val}
        if op == "neq":
            return f"{ref} != :{p_name}", {p_name: val}
        if op == "gt":
            return f"{ref} > :{p_name}", {p_name: val}
        if op == "gte":
            return f"{ref} >= :{p_name}", {p_name: val}
        if op == "lt":
            return f"{ref} < :{p_name}", {p_name: val}
        if op == "lte":
            return f"{ref} <= :{p_name}", {p_name: val}
        if op == "like":
            return f"{ref} ILIKE :{p_name}", {p_name: f"%{val}%"}
        if op == "in" and isinstance(val, (list, tuple)):
            p_dict = {}
            p_names = []
            for idx, item in enumerate(val):
                pn = f"p_{start_idx + idx}"
                p_names.append(f":{pn}")
                p_dict[pn] = item
            return f"{ref} IN ({', '.join(p_names)})", p_dict

        return f"{ref} = :{p_name}", {p_name: val}
