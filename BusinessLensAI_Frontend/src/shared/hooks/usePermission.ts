/**
 * RBAC Hook enforcing permissions across Executive, Business Manager, Business Analyst, Data Analyst, Admin
 */
import { useAuthStore } from '../stores/useAuthStore';
import { Role, PermissionAction, PermissionMatrix } from '@/shared/types';

const PERMISSION_MATRIX: PermissionMatrix = {
  EXECUTIVE: [
    'view_executive_dashboard',
    'use_ai_assistant',
    'export_reports',
  ],
  BUSINESS_MANAGER: [
    'view_executive_dashboard',
    'view_sales_dashboard',
    'view_inventory_dashboard',
    'view_forecast_dashboard',
    'use_ai_assistant',
    'export_reports',
  ],
  BUSINESS_ANALYST: [
    'view_executive_dashboard',
    'view_sales_dashboard',
    'view_inventory_dashboard',
    'view_forecast_dashboard',
    'use_ai_assistant',
    'build_custom_dashboard',
    'export_reports',
  ],
  DATA_ANALYST: [
    'view_executive_dashboard',
    'view_sales_dashboard',
    'view_inventory_dashboard',
    'view_forecast_dashboard',
    'use_ai_assistant',
    'build_custom_dashboard',
    'export_reports',
    'manage_database',
    'manage_mappings',
    'view_sql_reasoning',
    'access_sql_playground',
  ],
  ADMIN: [
    'view_executive_dashboard',
    'view_sales_dashboard',
    'view_inventory_dashboard',
    'view_forecast_dashboard',
    'use_ai_assistant',
    'build_custom_dashboard',
    'export_reports',
    'manage_database',
    'manage_mappings',
    'view_sql_reasoning',
    'access_sql_playground',
    'view_audit_logs',
    'manage_users',
    'manage_system_settings',
  ],
};

export function usePermission() {
  const user = useAuthStore((s) => s.user);
  const simulatedRole = useAuthStore((s) => s.simulatedRole);

  const currentRole: Role = simulatedRole || user?.role || 'EXECUTIVE';

  const can = (action: PermissionAction): boolean => {
    const allowedActions = PERMISSION_MATRIX[currentRole] || [];
    return allowedActions.includes(action);
  };

  const hasRole = (roleOrRoles: Role | Role[]): boolean => {
    if (Array.isArray(roleOrRoles)) {
      return roleOrRoles.includes(currentRole);
    }
    return currentRole === roleOrRoles;
  };

  const canAccessRoute = (allowedRoles?: Role[]): boolean => {
    if (!allowedRoles || allowedRoles.length === 0) return true;
    return allowedRoles.includes(currentRole);
  };

  return {
    currentRole,
    can,
    hasRole,
    canAccessRoute,
    isExecutive: currentRole === 'EXECUTIVE',
    isBusinessManager: currentRole === 'BUSINESS_MANAGER',
    isBusinessAnalyst: currentRole === 'BUSINESS_ANALYST',
    isDataAnalyst: currentRole === 'DATA_ANALYST',
    isAdmin: currentRole === 'ADMIN',
  };
}
