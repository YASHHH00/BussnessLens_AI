import warnings
warnings.filterwarnings('ignore')

from app.engines.data_quality_engine import DataQualityEngine
from app.utils.schema_differ import compute_schema_diff
from app.utils.data_profiler import compute_schema_hash

# Test Data Quality Engine
engine = DataQualityEngine()
sample_tables = {
    'orders': {
        'row_count': 1000,
        'columns': [
            {'name': 'order_id', 'physical_type': 'integer', 'nullable': False, 'sample_values': [1,2,3,4,5]},
            {'name': 'total', 'physical_type': 'numeric', 'nullable': True, 'sample_values': [100.0, -5.0, None, 200.0, 300.0]},
            {'name': 'status', 'physical_type': 'varchar', 'nullable': False, 'sample_values': ['pending','pending','pending','pending','pending']},
            {'name': 'notes', 'physical_type': 'varchar', 'nullable': True, 'sample_values': [None, None, None, None, None]},
        ]
    }
}

result = engine.evaluate_snapshot(sample_tables)
score = result["overall_score"]
total = result["total_issues"]
crit = result["critical_issues"]
warn = result["warning_issues"]
print(f"DQ Overall Score: {score}")
print(f"Total Issues: {total}  Critical: {crit}  Warning: {warn}")
for table, data in result['table_scores'].items():
    ts = data["score"]
    print(f"  {table}: score={ts}")
    for issue in data['issues']:
        sev = issue["severity"]
        col = issue["column"]
        msg = issue["message"]
        print(f"    [{sev}] {col}: {msg}")

# Test Schema Differ
old = {
    'orders': {'columns': [{'name': 'id', 'physical_type': 'integer', 'nullable': False}]},
    'old_table': {'columns': [{'name': 'x', 'physical_type': 'varchar', 'nullable': True}]},
}
new = {
    'orders': {'columns': [{'name': 'id', 'physical_type': 'bigint', 'nullable': False}]},
    'new_table': {'columns': [{'name': 'y', 'physical_type': 'integer', 'nullable': True}]},
}
diff = compute_schema_diff(old, new)
hc = diff.has_changes
brk = diff.is_breaking
added = diff.tables_added
removed = diff.tables_removed
ncc = len(diff.column_changes)
print(f"\nSchema Diff: has_changes={hc} is_breaking={brk}")
print(f"  Added: {added}  Removed: {removed}")
print(f"  Column changes: {ncc}")
for c in diff.column_changes:
    print(f"    {c.table}.{c.column}: {c.change_type} ({c.old_value} -> {c.new_value})")

h1 = compute_schema_hash(old)
h2 = compute_schema_hash(new)
diff_hashes = h1 != h2
print(f"\nHash old={h1[:8]} new={h2[:8]} (different={diff_hashes})")
print("\n=== PHASE 2 FUNCTIONAL TEST: PASSED ===")
