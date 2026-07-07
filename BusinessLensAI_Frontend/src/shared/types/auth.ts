/**
 * Authentication and Role-Based Access Control (RBAC) types
 */

export type Role = 
  | 'EXECUTIVE'
  | 'BUSINESS_MANAGER'
  | 'BUSINESS_ANALYST'
  | 'DATA_ANALYST'
  | 'ADMIN';

export interface User {
  id: string;
  email: string;
  name: string;
  role: Role;
  avatarUrl?: string;
  department?: string;
  createdAt: string;
  lastLoginAt: string;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresIn: number; // seconds
}

export interface LoginCredentials {
  email: string;
  password?: string;
  rememberMe?: boolean;
}

export interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export type PermissionAction =
  | 'view_executive_dashboard'
  | 'view_sales_dashboard'
  | 'view_inventory_dashboard'
  | 'view_forecast_dashboard'
  | 'use_ai_assistant'
  | 'build_custom_dashboard'
  | 'export_reports'
  | 'manage_database'
  | 'manage_mappings'
  | 'view_sql_reasoning'
  | 'access_sql_playground'
  | 'view_audit_logs'
  | 'manage_users'
  | 'manage_system_settings';

export type PermissionMatrix = Record<Role, PermissionAction[]>;
