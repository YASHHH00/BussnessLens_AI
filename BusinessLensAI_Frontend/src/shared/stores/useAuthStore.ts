/**
 * Zustand Auth Store managing user session, tokens, and Role Simulator overrides
 */
import { create } from 'zustand';
import { User, Role } from '@/shared/types';
import { authService } from '../lib/services/authService';
import { tokenStorage } from '../lib/apiClient';
import { setupMockAdapter } from '../lib/mockAdapter';

// Initialize mock adapter immediately when auth store loads
setupMockAdapter();

interface AuthStoreState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  simulatedRole: Role | null; // For Role Simulator testing widget
  
  // Actions
  login: (email: string, password?: string) => Promise<void>;
  logout: () => Promise<void>;
  checkSession: () => Promise<void>;
  setSimulatedRole: (role: Role | null) => void;
  clearError: () => void;
}

export const useAuthStore = create<AuthStoreState>((set, get) => ({
  user: {
    id: 'usr_001',
    email: 'admin@businesslens.ai',
    name: 'Alex Rivera',
    role: 'EXECUTIVE',
    department: 'Executive Leadership',
    createdAt: '2025-01-15T08:00:00Z',
    lastLoginAt: new Date().toISOString(),
  },
  isAuthenticated: true, // Default to authenticated for demo/evaluation
  isLoading: false,
  error: null,
  simulatedRole: null,

  login: async (email: string, password?: string) => {
    set({ isLoading: true, error: null });
    try {
      const { user } = await authService.login({ email, password });
      set({ user, isAuthenticated: true, isLoading: false, simulatedRole: null });
    } catch (err: unknown) {
      const message = err && typeof err === 'object' && 'message' in err ? String(err.message) : 'Login failed. Please check credentials.';
      set({ error: message, isLoading: false, isAuthenticated: false, user: null });
      throw err;
    }
  },

  logout: async () => {
    set({ isLoading: true });
    try {
      await authService.logout();
    } finally {
      tokenStorage.clearTokens();
      set({ user: null, isAuthenticated: false, isLoading: false, simulatedRole: null });
    }
  },

  checkSession: async () => {
    const token = tokenStorage.getAccessToken();
    if (!token && !get().isAuthenticated) {
      set({ isAuthenticated: false, user: null });
      return;
    }
    try {
      set({ isLoading: true });
      const user = await authService.getCurrentUser();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch {
      tokenStorage.clearTokens();
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  setSimulatedRole: (role: Role | null) => {
    set({ simulatedRole: role });
  },

  clearError: () => set({ error: null }),
}));
