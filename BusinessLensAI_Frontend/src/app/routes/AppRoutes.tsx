import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { MainLayout } from '../layout/MainLayout';
import { ProtectedRoute } from './ProtectedRoute';
import { UnauthorizedPage } from './UnauthorizedPage';
import { NotFoundPage } from './NotFoundPage';

// Feature Pages
import { LoginPage } from '../../features/auth/LoginPage';
import { HomePage } from '../../features/home/HomePage';
import { ProfilePage } from '../../features/profile/ProfilePage';
import { ConnectDatabasePage } from '../../features/connection/ConnectDatabasePage';
import { SchemaDetectionPage } from '../../features/connection/SchemaDetectionPage';
import { MappingPage } from '../../features/mapping/MappingPage';
import { SemanticExplorerPage } from '../../features/semantic/SemanticExplorerPage';
import { RecommendationsPage } from '../../features/recommendations/RecommendationsPage';
import { DashboardPage } from '../../features/dashboard/DashboardPage';
import { DataQualityReportPage } from '../../features/quality/DataQualityReportPage';
import { BusinessRulesPage } from '../../features/rules/BusinessRulesPage';
import { AIAssistantPage } from '../../features/ai/AIAssistantPage';
import { SqlPlaygroundPage } from '../../features/sql/SqlPlaygroundPage';
import { ReportsPage } from '../../features/reports/ReportsPage';
import { AdminPage } from '../../features/admin/AdminPage';

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Public / Auth Route */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/unauthorized" element={<UnauthorizedPage />} />

      {/* Protected Layout Routes */}
      <Route element={<ProtectedRoute />}>
        <Route element={<MainLayout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/connect" element={<ConnectDatabasePage />} />
          <Route path="/schema-detection" element={<SchemaDetectionPage />} />
          <Route path="/mapping" element={<MappingPage />} />
          <Route path="/semantic-explorer" element={<SemanticExplorerPage />} />
          <Route path="/recommendations" element={<RecommendationsPage />} />
          <Route path="/dashboards" element={<Navigate to="/dashboards/executive" replace />} />
          <Route path="/dashboards/:category" element={<DashboardPage />} />
          <Route path="/quality" element={<DataQualityReportPage />} />
          <Route path="/rules" element={<BusinessRulesPage />} />
          <Route path="/ai-assistant" element={<AIAssistantPage />} />
          <Route path="/reports" element={<ReportsPage />} />

          {/* Role-Restricted Routes */}
          <Route element={<ProtectedRoute requiredPermission="access_sql_playground" />}>
            <Route path="/sql-playground" element={<SqlPlaygroundPage />} />
          </Route>

          <Route element={<ProtectedRoute requiredPermission="view_audit_logs" />}>
            <Route path="/admin" element={<AdminPage />} />
          </Route>
        </Route>
      </Route>

      {/* Fallback 404 Route */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
};
