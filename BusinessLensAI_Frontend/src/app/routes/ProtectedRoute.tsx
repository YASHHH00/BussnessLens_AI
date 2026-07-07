import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../shared/stores/useAuthStore';
import { usePermission } from '../../shared/hooks/usePermission';
import { PermissionAction } from '../../shared/types';

export interface ProtectedRouteProps {
  requiredPermission?: PermissionAction;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ requiredPermission }) => {
  const { isAuthenticated, user } = useAuthStore();
  const { can } = usePermission();
  const location = useLocation();

  // If not logged in, redirect to login page preserving intended destination
  if (!isAuthenticated || !user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // If route requires specific permission action, check RBAC matrix
  if (requiredPermission && !can(requiredPermission)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <Outlet />;
};
