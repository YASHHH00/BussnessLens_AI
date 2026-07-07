import { apiClient } from '../apiClient';
import * as Types from '../../types';

export const semanticService = {
  async getSemanticFields(connectionId = 'conn_pg_01'): Promise<Types.SemanticField[]> {
    const response = await apiClient.get(`/semantic/fields?connectionId=${connectionId}`);
    return response.data.data;
  },

  async getDomains(): Promise<Types.SemanticDomain[]> {
    const response = await apiClient.get('/semantic/domains');
    return response.data.data;
  },

  async updateFieldStatus(fieldId: string, status: Types.SemanticField['currentStatus']): Promise<Types.SemanticField> {
    const response = await apiClient.patch(`/semantic/fields/${fieldId}`, { status });
    return response.data.data;
  },
};
