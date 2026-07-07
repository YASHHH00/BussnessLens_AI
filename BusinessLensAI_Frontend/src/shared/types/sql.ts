export interface SqlExecutionResult {
  columns: string[];
  rows: Record<string, unknown>[];
  executionTimeMs: number;
  rowCount: number;
}
