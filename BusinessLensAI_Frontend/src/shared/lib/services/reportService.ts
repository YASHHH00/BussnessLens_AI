import { apiClient } from '../apiClient';
import * as Types from '../../types';

export const reportService = {
  async getReports(): Promise<Types.ReportJob[]> {
    const response = await apiClient.get('/reports');
    return response.data.data || [
      { id: 'rep_01', title: 'Q2 Executive Summary & Revenue Breakdown', sourceDashboardId: 'dash_exec', sourceDashboardTitle: 'Executive Summary', format: 'PDF', status: 'READY', createdAt: new Date(Date.now() - 1000 * 3600 * 2).toISOString(), downloadUrl: '#', fileSizeKb: 2450 },
      { id: 'rep_02', title: 'Inventory Stockout Risk Analysis', sourceDashboardId: 'dash_inv', sourceDashboardTitle: 'Inventory Dashboard', format: 'EXCEL', status: 'READY', createdAt: new Date(Date.now() - 1000 * 3600 * 5).toISOString(), downloadUrl: '#', fileSizeKb: 1820 },
      { id: 'rep_03', title: 'Regional Customer Segment Export', sourceDashboardId: 'dash_cust', sourceDashboardTitle: 'Customer Dashboard', format: 'CSV', status: 'GENERATING', createdAt: new Date(Date.now() - 1000 * 60 * 3).toISOString() },
    ];
  },

  async triggerReportExport(dashboardId: string, format: Types.ReportFormat): Promise<Types.ReportJob> {
    const response = await apiClient.post('/reports/export', { dashboardId, format });
    return response.data.data || {
      id: `rep_${Date.now()}`,
      title: `Export ${format} - ${new Date().toLocaleDateString()}`,
      sourceDashboardId: dashboardId,
      sourceDashboardTitle: 'Custom Export',
      format,
      status: 'GENERATING',
      createdAt: new Date().toISOString(),
    };
  },
};
