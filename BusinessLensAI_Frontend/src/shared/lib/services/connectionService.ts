import { apiClient } from '../apiClient';
import * as Types from '../../types';

export const connectionService = {
  async getConnections(): Promise<Types.DatabaseConnection[]> {
    const response = await apiClient.get('/connections');
    return response.data.data;
  },

  async testConnection(formValues: Types.DBConnectionFormValues): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.post('/connections/test', formValues);
    return response.data.data;
  },

  async saveConnection(formValues: Types.DBConnectionFormValues): Promise<Types.DatabaseConnection> {
    const response = await apiClient.post('/connections', formValues);
    return response.data.data;
  },

  async uploadFile(file: File): Promise<Types.FileUploadMetadata> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post('/connections/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data.data;
  },
};
