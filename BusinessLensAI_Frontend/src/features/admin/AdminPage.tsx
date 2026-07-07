import React, { useState, useEffect } from 'react';
import { ShieldAlert, Search, Filter, ShieldCheck, UserCheck, Lock, AlertTriangle, CheckCircle2, Clock, Users, Database } from 'lucide-react';
import { Button, Input, Select, Card, CardHeader, CardTitle, CardDescription, CardContent, Badge, DataTable, toast, DomainSelector } from '../../shared/components';
import { adminService } from '../../shared/lib/services/adminService';
import { AuditLogEntry, Role } from '../../shared/types';

export const AdminPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'audit' | 'users' | 'system'>('audit');
  const [logs, setLogs] = useState<AuditLogEntry[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [filterAction, setFilterAction] = useState<string>('ALL');

  useEffect(() => {
    setIsLoading(true);
    adminService
      .getAuditLogs()
      .then((data) => {
        setLogs(data);
        setIsLoading(false);
      })
      .catch(() => setIsLoading(false));
  }, []);

  const filteredLogs = logs.filter((log) => (filterAction === 'ALL' ? true : log.actionType === filterAction));

  const mockUsers = [
    { id: 'u_01', name: 'Alex Rivera', email: 'admin@businesslens.ai', role: 'EXECUTIVE' as Role, status: 'ACTIVE', dept: 'Executive Leadership' },
    { id: 'u_02', name: 'Sarah Jenkins', email: 's.jenkins@businesslens.ai', role: 'BUSINESS_MANAGER' as Role, status: 'ACTIVE', dept: 'Sales & Revenue' },
    { id: 'u_03', name: 'Michael Chang', email: 'm.chang@businesslens.ai', role: 'BUSINESS_ANALYST' as Role, status: 'ACTIVE', dept: 'BI & Analytics' },
    { id: 'u_04', name: 'David Vance', email: 'd.vance@businesslens.ai', role: 'DATA_ANALYST' as Role, status: 'ACTIVE', dept: 'Data Engineering' },
    { id: 'u_05', name: 'Elena Rostova', email: 'e.rostova@businesslens.ai', role: 'ADMIN' as Role, status: 'ACTIVE', dept: 'Platform Security' },
  ];

  const getSeverityBadge = (sev: string) => {
    switch (sev) {
      case 'CRITICAL':
        return <Badge variant="danger">Critical</Badge>;
      case 'WARNING':
        return <Badge variant="warning">Warning</Badge>;
      case 'INFO':
      default:
        return <Badge variant="info">Info</Badge>;
    }
  };

  const columns = [
    {
      key: 'timestamp',
      header: 'Timestamp',
      render: (row: any) => <span className="font-mono text-muted-foreground">{new Date(row.timestamp).toLocaleTimeString()}</span>,
    },
    {
      key: 'userName',
      header: 'User Account',
      render: (row: any) => (
        <div>
          <div className="font-bold text-foreground">{row.userName}</div>
          <span className="text-[10px] text-primary font-semibold">{row.userRole}</span>
        </div>
      ),
    },
    {
      key: 'actionType',
      header: 'Action Type',
      render: (row: any) => <Badge variant="outline" size="sm" className="font-mono">{row.actionType}</Badge>,
    },
    { key: 'details', header: 'Event Details', render: (row: any) => <span className="text-foreground">{row.details}</span> },
    { key: 'targetResource', header: 'Target Resource', render: (row: any) => <code className="font-mono bg-muted px-1.5 py-0.5 rounded text-xs">{row.targetResource}</code> },
    { key: 'severity', header: 'Severity', render: (row: any) => getSeverityBadge(row.severity) },
    {
      key: 'status',
      header: 'Status',
      render: (row: any) => (
        <Badge variant={row.status === 'SUCCESS' ? 'success' : 'danger'} size="sm">
          {row.status}
        </Badge>
      ),
    },
  ];

  return (
    <div className="space-y-8 max-w-7xl mx-auto animate-in fade-in-50 duration-300 pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Badge variant="danger">Strictly Admin Access</Badge>
            <DomainSelector />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">System Administration & Audit Logs</h1>
          <p className="text-sm text-muted-foreground">
            SOC2 Type II compliance audit trail, user RBAC governance, and platform security telemetry.
          </p>
        </div>

        {/* Tab switchers */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-muted/60 border border-border">
          <button
            onClick={() => setActiveTab('audit')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'audit' ? 'bg-primary text-primary-foreground shadow-sm font-bold' : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Audit Logs ({logs.length})
          </button>
          <button
            onClick={() => setActiveTab('users')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'users' ? 'bg-primary text-primary-foreground shadow-sm font-bold' : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            User RBAC Governance
          </button>
          <button
            onClick={() => setActiveTab('system')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'system' ? 'bg-primary text-primary-foreground shadow-sm font-bold' : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            System Security
          </button>
        </div>
      </div>

      {activeTab === 'audit' && (
        <div className="space-y-6">
          {/* Top filter bar */}
          <Card className="bg-muted/20 border-border">
            <CardContent className="p-4 flex flex-wrap items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Filter Action:</span>
                <Select value={filterAction} onChange={(e) => setFilterAction(e.target.value)} className="w-48 h-8 text-xs py-0">
                  <option value="ALL">All Action Types</option>
                  <option value="LOGIN">LOGIN</option>
                  <option value="DB_CONNECT">DB_CONNECT</option>
                  <option value="SCHEMA_SCAN">SCHEMA_SCAN</option>
                  <option value="MAPPING_CONFIRM">MAPPING_CONFIRM</option>
                  <option value="DASHBOARD_GEN">DASHBOARD_GEN</option>
                  <option value="AI_QUERY">AI_QUERY</option>
                  <option value="EXPORT">EXPORT</option>
                </Select>
              </div>
              <Badge variant="success">SOC2 Type II Immutable Logging</Badge>
            </CardContent>
          </Card>

          {/* Audit Table */}
          <DataTable
            data={filteredLogs}
            columns={columns}
            searchKey="details"
            searchPlaceholder="Search audit log details or user name..."
            pageSize={10}
          />
        </div>
      )}

      {activeTab === 'users' && (
        <Card className="overflow-hidden border-border/80">
          <CardHeader className="p-6 pb-4 border-b border-border flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-base">Platform User Accounts & Role Governance</CardTitle>
              <CardDescription>Manage RBAC permissions across the 5 enterprise roles</CardDescription>
            </div>
            <Button variant="primary" size="sm" onClick={() => toast.info('Add User', 'User invitation workflow triggered.')}>
              Invite New User
            </Button>
          </CardHeader>
          <CardContent className="p-0 overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead className="bg-muted/60 border-b border-border text-muted-foreground select-none">
                <tr>
                  <th className="p-4 font-semibold uppercase tracking-wider">User Account</th>
                  <th className="p-4 font-semibold uppercase tracking-wider">Department</th>
                  <th className="p-4 font-semibold uppercase tracking-wider">Assigned RBAC Role</th>
                  <th className="p-4 font-semibold uppercase tracking-wider">Account Status</th>
                  <th className="p-4 font-semibold uppercase tracking-wider text-right">Governance Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border bg-card">
                {mockUsers.map((u) => (
                  <tr key={u.id} className="hover:bg-muted/20 transition-colors">
                    <td className="p-4">
                      <div className="font-bold text-foreground">{u.name}</div>
                      <span className="text-[11px] font-mono text-muted-foreground">{u.email}</span>
                    </td>
                    <td className="p-4 text-foreground font-medium">{u.dept}</td>
                    <td className="p-4">
                      <Badge variant="purple" size="sm">{u.role}</Badge>
                    </td>
                    <td className="p-4">
                      <Badge variant="success" size="sm">{u.status}</Badge>
                    </td>
                    <td className="p-4 text-right">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => toast.success('Permissions Updated', `Role governance verified for ${u.name}.`)}
                        className="h-8 text-xs font-semibold"
                      >
                        Edit Permissions
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      )}

      {activeTab === 'system' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Enterprise Security Compliance</CardTitle>
              <CardDescription>Active encryption and data residency controls</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 text-xs">
              <div className="flex justify-between p-3 rounded-lg bg-muted/40 border border-border">
                <span className="text-muted-foreground">TLS Encryption in Transit:</span>
                <Badge variant="success">256-bit AES Enabled</Badge>
              </div>
              <div className="flex justify-between p-3 rounded-lg bg-muted/40 border border-border">
                <span className="text-muted-foreground">Database Transaction Guard:</span>
                <Badge variant="success">Read-Only Enforced</Badge>
              </div>
              <div className="flex justify-between p-3 rounded-lg bg-muted/40 border border-border">
                <span className="text-muted-foreground">SOC2 Type II Audit Logging:</span>
                <Badge variant="success">Active (100% Coverage)</Badge>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Redis Cache & Memory Health</CardTitle>
              <CardDescription>In-memory dashboard acceleration metrics</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 text-xs">
              <div className="flex justify-between p-3 rounded-lg bg-muted/40 border border-border">
                <span className="text-muted-foreground">Redis Memory Utilization:</span>
                <span className="font-mono font-bold text-foreground">14.8 MB / 512 MB (2.8%)</span>
              </div>
              <div className="flex justify-between p-3 rounded-lg bg-muted/40 border border-border">
                <span className="text-muted-foreground">Cache Hit Ratio (24h):</span>
                <span className="font-mono font-bold text-emerald-500">98.4%</span>
              </div>
              <div className="flex justify-between p-3 rounded-lg bg-muted/40 border border-border">
                <span className="text-muted-foreground">Average Query Latency:</span>
                <span className="font-mono font-bold text-primary">18ms</span>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};
