import { apiClient } from '../apiClient';
import * as Types from '../../types';

export const dashboardService = {
  async getDashboards(): Promise<Types.Dashboard[]> {
    const response = await apiClient.get('/dashboards');
    return response.data.data;
  },

  async getDashboardById(id: string): Promise<Types.Dashboard> {
    const response = await apiClient.get(`/dashboards/${id}`);
    return response.data.data;
  },

  async saveCustomDashboard(dashboard: Partial<Types.Dashboard>): Promise<Types.Dashboard> {
    const response = await apiClient.post('/dashboards', dashboard);
    return response.data.data;
  },

  async getVersionHistory(dashboardId: string): Promise<Types.DashboardVersion[]> {
    const response = await apiClient.get(`/dashboards/${dashboardId}/versions`);
    return response.data.data;
  },

  async restoreVersion(dashboardId: string, versionId: string): Promise<Types.Dashboard> {
    const response = await apiClient.post(`/dashboards/${dashboardId}/restore`, { versionId });
    return response.data.data;
  },

  async refreshRedisCache(dashboardId: string): Promise<Types.RedisCacheStatus> {
    const response = await apiClient.post(`/dashboards/${dashboardId}/cache-refresh`);
    return response.data.data;
  },

  async getRecommendedDashboards(connectionId?: string): Promise<Types.Dashboard[]> {
    const response = await apiClient.get('/dashboards', { params: { connectionId, recommended: true } });
    return response.data.data || [];
  },

  async generateDashboards(selectedIds: string[]): Promise<Types.Dashboard[]> {
    const response = await apiClient.post('/dashboards/generate', { selectedIds });
    return response.data.data || [];
  },
};
