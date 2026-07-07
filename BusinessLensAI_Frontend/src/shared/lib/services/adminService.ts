import { apiClient } from '../apiClient';
import * as Types from '../../types';

export const adminService = {
  async getUsers(): Promise<Types.AdminUserManage[]> {
    const response = await apiClient.get('/admin/users');
    return response.data.data || [
      { id: 'usr_001', name: 'Alex Rivera', email: 'admin@businesslens.ai', role: 'EXECUTIVE', isActive: true, createdAt: '2025-01-15T08:00:00Z', lastLogin: 'Just now' },
      { id: 'usr_002', name: 'Sarah Jenkins', email: 's.jenkins@businesslens.ai', role: 'DATA_ANALYST', isActive: true, createdAt: '2025-02-10T11:30:00Z', lastLogin: '5 mins ago' },
      { id: 'usr_003', name: 'Marcus Vance', email: 'm.vance@businesslens.ai', role: 'ADMIN', isActive: true, createdAt: '2025-01-01T00:00:00Z', lastLogin: '1 hour ago' },
      { id: 'usr_004', name: 'Elena Rostova', email: 'e.rostova@businesslens.ai', role: 'BUSINESS_ANALYST', isActive: true, createdAt: '2025-03-01T09:15:00Z', lastLogin: '1 day ago' },
      { id: 'usr_005', name: 'David Kim', email: 'd.kim@businesslens.ai', role: 'BUSINESS_MANAGER', isActive: true, createdAt: '2025-03-12T14:20:00Z', lastLogin: '2 days ago' },
    ];
  },

  async updateUserRole(userId: string, role: Types.Role): Promise<{ success: boolean }> {
    const response = await apiClient.patch(`/admin/users/${userId}/role`, { role });
    return response.data.data || { success: true };
  },

  async getAuditLogs(filters?: Record<string, unknown>): Promise<Types.SystemAuditLog[]> {
    const response = await apiClient.get('/audit-logs', { params: filters });
    return response.data.data || [];
  },
};
