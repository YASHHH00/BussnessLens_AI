/**
 * Admin Management and Audit Logs types (Backend V3 Aligned)
 */

import { Role } from './auth';
import { DBType } from './connection';

export interface AdminUserManage {
  id: string;
  name: string;
  email: string;
  role: Role;
  isActive: boolean;
  createdAt: string;
  lastLogin: string;
}

export interface AdminConnectionManage {
  id: string;
  name: string;
  type: DBType;
  host: string;
  status: string;
  ownerEmail: string;
  lastScannedAt: string;
}

export interface AdminMappingManage {
  id: string;
  connectionId: string;
  connectionName: string;
  totalMappings: number;
  confirmedMappings: number;
  lastModifiedBy: string;
  lastModifiedAt: string;
}

export type AuditActionType = 
  | 'LOGIN'
  | 'DB_CONNECT'
  | 'SCHEMA_SCAN'
  | 'MAPPING_CHANGE'
  | 'DASHBOARD_GEN'
  | 'FORECAST_REQUEST'
  | 'AI_QUERY'
  | 'EXPORT';

export type AuditSeverity = 'INFO' | 'WARNING' | 'CRITICAL';

export interface SystemAuditLog {
  id: string;
  timestamp: string;
  userId: string;
  userName: string;
  userRole: Role;
  action: AuditActionType;
  actionType?: string;
  severity: AuditSeverity;
  description: string;
  details?: string;
  targetResource?: string;
  status?: string;
  ipAddress: string;
  metadata?: Record<string, unknown>;
  [key: string]: any;
}

export type AuditLogEntry = SystemAuditLog;
