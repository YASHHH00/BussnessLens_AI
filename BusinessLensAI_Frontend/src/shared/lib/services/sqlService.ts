import { apiClient } from '../apiClient';

export interface SqlExecutionResult {
  columns: string[];
  rows: Record<string, unknown>[];
  executionTimeMs: number;
  rowCount: number;
}

export const sqlService = {
  async executeReadonlyQuery(query: string, connectionId = 'conn_pg_01'): Promise<SqlExecutionResult> {
    const response = await apiClient.post('/sql/execute', { query, connectionId });
    return response.data.data;
  },

  async getQueryHistory(): Promise<{ id: string; query: string; timestamp: string; status: 'SUCCESS' | 'ERROR' }[]> {
    const response = await apiClient.get('/sql/history');
    return response.data.data || [];
  },
};
