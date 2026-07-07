import { apiClient } from '../apiClient';
import * as Types from '../../types';

export const qualityService = {
  async getDataQualityReport(connectionId = 'conn_pg_01'): Promise<Types.DataQualityReport> {
    const response = await apiClient.get(`/quality/report?connectionId=${connectionId}`);
    return response.data.data;
  },

  async runQualityScan(connectionId = 'conn_pg_01'): Promise<Types.DataQualityReport> {
    const response = await apiClient.post(`/quality/scan`, { connectionId });
    return response.data.data;
  },
};
