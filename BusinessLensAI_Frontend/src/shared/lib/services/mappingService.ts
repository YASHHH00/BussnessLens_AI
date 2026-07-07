import { apiClient } from '../apiClient';
import * as Types from '../../types';

export const mappingService = {
  async getMappings(connectionId = 'conn_pg_01'): Promise<Types.ColumnMapping[]> {
    const response = await apiClient.get(`/mappings?connectionId=${connectionId}`);
    return response.data.data;
  },

  async confirmMapping(mappingId: string): Promise<Types.ColumnMapping> {
    const response = await apiClient.post(`/mappings/${mappingId}/confirm`);
    return response.data.data;
  },

  async saveAllMappings(mappings: Types.ColumnMapping[]): Promise<{ success: boolean; count: number }> {
    const response = await apiClient.post('/mappings/save', { mappings });
    return response.data.data;
  },

  async getSuggestedKPIs(): Promise<Types.SuggestedKPI[]> {
    const response = await apiClient.get('/recommendations/kpis');
    return response.data.data;
  },

  async getSchemaDriftAlerts(connectionId = 'conn_pg_01'): Promise<Types.SchemaDriftAlert | null> {
    const response = await apiClient.get(`/mappings/drift?connectionId=${connectionId}`);
    return response.data.data || null;
  },
};
