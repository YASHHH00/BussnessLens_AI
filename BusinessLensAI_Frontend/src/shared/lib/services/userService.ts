import { apiClient } from '../apiClient';
import * as Types from '../../types';

export const userService = {
  async getUserProfile(): Promise<Types.User> {
    const response = await apiClient.get('/auth/me');
    return response.data.data;
  },

  async updateProfile(values: Types.UserProfileFormValues): Promise<Types.User> {
    const response = await apiClient.put('/users/profile', values);
    return response.data.data;
  },

  async changePassword(values: Types.PasswordChangeFormValues): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.post('/users/change-password', values);
    return response.data.data || { success: true, message: 'Password updated successfully.' };
  },
};
