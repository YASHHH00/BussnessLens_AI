import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { Database, Search, GitMerge, Layers, Sparkles, BarChart3, TrendingUp, Code2, FileText, ShieldAlert, Home, User, Settings } from 'lucide-react';
import { useAppStore, WORKFLOW_STEPS_LIST, WorkflowStep } from '../../shared/stores/useAppStore';
import { usePermission } from '../../shared/hooks/usePermission';
import { Badge } from '../../shared/components';

export const Sidebar: React.FC = () => {
  const isSidebarOpen = useAppStore((s) => s.isSidebarOpen);
  const currentStep = useAppStore((s) => s.currentWorkflowStep);
  const setWorkflowStep = useAppStore((s) => s.setWorkflowStep);
  const location = useLocation();
  const { can, currentRole } = usePermission();

  if (!isSidebarOpen) return null;

  interface NavItem {
    label: string;
    path: string;
    icon: React.ReactElement;
    step?: WorkflowStep;
    requiredRole?: string;
  }

  const navGroups: { title: string; items: NavItem[] }[] = [
    {
      title: 'Analytics Platform',
      items: [
        { label: 'Platform Home', path: '/', icon: <Home className="w-4 h-4" /> },
        { label: 'Account & Settings', path: '/profile', icon: <User className="w-4 h-4" /> },
      ],
    },
    {
      title: 'Data Connection & Schema (Steps 1-4)',
      items: [
        { label: '1. Connect Database', path: '/connect', icon: <Database className="w-4 h-4" />, step: 'CONNECT_DB' as WorkflowStep, requiredRole: 'manage_database' },
        { label: '2. Schema Detection', path: '/schema-detection', icon: <Search className="w-4 h-4" />, step: 'SCHEMA_DETECT' as WorkflowStep, requiredRole: 'manage_database' },
        { label: '4. Mapping Review', path: '/mapping', icon: <GitMerge className="w-4 h-4" />, step: 'MAPPING_REVIEW' as WorkflowStep, requiredRole: 'manage_mappings' },
      ],
    },
    {
      title: 'Semantic & Dashboards (Steps 5-7)',
      items: [
        { label: '5. Semantic Explorer', path: '/semantic-explorer', icon: <Layers className="w-4 h-4 text-blue-500" />, step: 'SEMANTIC_LAYER' as WorkflowStep },
        { label: '6. Recommendations', path: '/recommendations', icon: <Sparkles className="w-4 h-4 text-purple-500" />, step: 'RECOMMENDED_DASHBOARDS' as WorkflowStep },
        { label: '7. Dashboards', path: '/dashboards/executive', icon: <BarChart3 className="w-4 h-4 text-primary" />, step: 'DASHBOARD_GEN' as WorkflowStep },
      ],
    },
    {
      title: 'AI Intelligence & Export (Steps 8-10)',
      items: [
        { label: '8. AI Insights & Q&A', path: '/ai-assistant', icon: <Sparkles className="w-4 h-4 text-purple-500" />, step: 'INSIGHTS' as WorkflowStep },
        { label: '9. 90-Day Forecasting', path: '/dashboards/forecast', icon: <TrendingUp className="w-4 h-4 text-emerald-500" />, step: 'FORECAST' as WorkflowStep },
        { label: '10. Report Exporter', path: '/reports', icon: <FileText className="w-4 h-4 text-amber-500" />, step: 'REPORTS' as WorkflowStep },
      ],
    },
    {
      title: 'Advanced & Administration',
      items: [
        { label: 'SQL Playground', path: '/sql-playground', icon: <Code2 className="w-4 h-4 text-emerald-500" />, requiredRole: 'access_sql_playground' },
        { label: 'System Audit Logs', path: '/admin', icon: <ShieldAlert className="w-4 h-4 text-destructive" />, requiredRole: 'view_audit_logs' },
      ],
    },
  ];

  return (
    <aside className="w-64 shrink-0 border-r border-border bg-card/60 backdrop-blur-md h-[calc(100vh-4rem)] sticky top-16 overflow-y-auto hidden md:flex flex-col justify-between p-4 shadow-sm">
      <div className="space-y-6">
        {/* Active Role Banner */}
        <div className="p-3 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-between">
          <div className="space-y-0.5">
            <span className="text-[10px] font-bold uppercase tracking-wider text-primary">Active RBAC Role</span>
            <div className="text-xs font-extrabold text-foreground">{currentRole}</div>
          </div>
          <Badge variant="purple" size="sm">Verified</Badge>
        </div>

        {/* Navigation Groups */}
        <div className="space-y-6">
          {navGroups.map((group, gIdx) => (
            <div key={gIdx} className="space-y-1.5">
              <h4 className="px-2 text-[10px] font-bold text-muted-foreground uppercase tracking-wider">{group.title}</h4>
              <nav className="space-y-1">
                {group.items.map((item, idx) => {
                  // If item requires a permission action, check if role has it
                  const isRestricted = item.requiredRole && !can(item.requiredRole as unknown as Parameters<typeof can>[0]);

                  const isActive = location.pathname === item.path || (item.step && currentStep === item.step);

                  return (
                    <NavLink
                      key={idx}
                      to={item.path}
                      onClick={() => {
                        if (item.step) setWorkflowStep(item.step);
                      }}
                      className={`flex items-center justify-between px-3 py-2 rounded-lg text-xs font-semibold transition-all duration-200 ${
                        isActive
                          ? 'bg-primary text-primary-foreground shadow-sm font-bold'
                          : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                      }`}
                    >
                      <div className="flex items-center gap-2.5 truncate">
                        <span className="shrink-0">{item.icon}</span>
                        <span className="truncate">{item.label}</span>
                      </div>

                      {isRestricted && (
                        <Badge variant="outline" size="sm" className="text-[9px] px-1 py-0 border-amber-500/30 text-amber-500">
                          Gate
                        </Badge>
                      )}
                    </NavLink>
                  );
                })}
              </nav>
            </div>
          ))}
        </div>
      </div>

      {/* Bottom info */}
      <div className="pt-4 border-t border-border mt-6 text-center">
        <span className="text-[11px] text-muted-foreground">
          Connected: <strong className="text-foreground">PostgreSQL Prod</strong>
        </span>
      </div>
    </aside>
  );
};
