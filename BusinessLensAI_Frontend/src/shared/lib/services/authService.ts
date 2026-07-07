import { apiClient, tokenStorage } from '../apiClient';
import * as Types from '../../types';

export const authService = {
  async login(credentials: Types.LoginCredentials): Promise<{ user: Types.User; tokens: Types.AuthTokens }> {
    const response = await apiClient.post('/auth/login', credentials);
    const { user, tokens } = response.data.data;
    tokenStorage.setTokens(tokens.accessToken, tokens.refreshToken);
    return { user, tokens };
  },

  async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout');
    } finally {
      tokenStorage.clearTokens();
    }
  },

  async getCurrentUser(): Promise<Types.User> {
    const response = await apiClient.get('/auth/me');
    return response.data.data;
  },
};
