import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell, Plus, ShieldAlert, CheckCircle2, AlertTriangle, ArrowLeft, Trash2, Edit2, Zap } from 'lucide-react';
import { Button, Input, Select, Card, CardHeader, CardTitle, CardDescription, CardContent, Badge, Modal, toast, LoadingState, DomainSelector } from '../../shared/components';
import { rulesService } from '../../shared/lib/services/rulesService';
import { BusinessRule } from '../../shared/types';

export const BusinessRulesPage: React.FC = () => {
  const navigate = useNavigate();
  const [rules, setRules] = useState<BusinessRule[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

  // New rule form state
  const [name, setName] = useState('');
  const [targetMetric, setTargetMetric] = useState('inventory_count');
  const [condition, setCondition] = useState<BusinessRule['condition']>('LESS_THAN');
  const [threshold, setThreshold] = useState('50');
  const [severity, setSeverity] = useState<BusinessRule['severity']>('WARNING');

  useEffect(() => {
    setIsLoading(true);
    rulesService
      .getRules('conn_pg_01')
      .then((data: BusinessRule[]) => {
        setRules(data);
        setIsLoading(false);
      })
      .catch(() => setIsLoading(false));
  }, []);

  const toggleRuleActive = async (id: string, currentStatus: boolean) => {
    setRules((prev) => prev.map((r) => (r.id === id ? { ...r, isActive: !currentStatus } : r)));
    toast.info('Rule Status Updated', `Business rule has been ${!currentStatus ? 'activated' : 'deactivated'}.`);
  };

  const deleteRule = async (id: string) => {
    setRules((prev) => prev.filter((r) => r.id !== id));
    toast.success('Rule Deleted', 'Business rule removed from active evaluation engine.');
  };

  const handleCreateRule = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      toast.error('Validation Error', 'Rule name is required.');
      return;
    }

    const newRule: BusinessRule = {
      id: `rule_${Date.now()}`,
      name: name.trim(),
      targetMetric,
      condition,
      thresholdValue: Number(threshold) || 0,
      severity,
      notificationDestination: 'In-App Toast & Email',
      isActive: true,
    };

    try {
      const saved = await rulesService.createRule(newRule);
      setRules((prev) => [saved, ...prev]);
      toast.success('Rule Created', `${saved.name} is now monitoring live data stream.`);
      setName('');
      setIsModalOpen(false);
    } catch {
      toast.error('Create Failed', 'Could not save business rule.');
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto animate-in fade-in-50 duration-300 pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Badge variant="purple">Backend V3: Business Rules Engine</Badge>
            <DomainSelector />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">Business Rules & Anomaly Alerts</h1>
          <p className="text-sm text-muted-foreground">
            Define automated threshold alerts and real-time operational triggers evaluated against live PostgreSQL metrics.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button variant="outline" size="md" onClick={() => navigate('/dashboards/executive')} leftIcon={<ArrowLeft className="w-4 h-4" />}>
            Back to Dashboards
          </Button>
          <Button variant="primary" size="md" onClick={() => setIsModalOpen(true)} leftIcon={<Plus className="w-4 h-4" />}>
            Create New Rule
          </Button>
        </div>
      </div>

      {/* Top Banner */}
      <Card className="border-blue-500/30 bg-gradient-to-r from-card via-card to-blue-500/10">
        <CardContent className="p-6 flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-2xl bg-blue-500/10 text-blue-500 shadow-inner">
              <Zap className="w-8 h-8 animate-pulse" />
            </div>
            <div className="space-y-1">
              <h3 className="text-lg font-bold text-foreground">Real-Time Evaluation Engine Active</h3>
              <p className="text-xs text-muted-foreground max-w-xl leading-relaxed">
                Rules are evaluated every 60 seconds against incoming database transactions. When thresholds are breached, notifications are dispatched to configured email and in-app channels.
              </p>
            </div>
          </div>
          <Badge variant="info" size="md">3 Active Rules Monitoring</Badge>
        </CardContent>
      </Card>

      {/* Rules List Table */}
      <Card className="overflow-hidden border-border/80">
        <CardHeader className="p-6 pb-4 border-b border-border flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-base">Configured Business Rules</CardTitle>
            <CardDescription>Manage alert criteria and notification routing</CardDescription>
          </div>
          <Badge variant="success">All Systems Operational</Badge>
        </CardHeader>
        <CardContent className="p-0 overflow-x-auto">
          {isLoading ? (
            <div className="p-6">
              <LoadingState type="table" count={4} />
            </div>
          ) : rules.length === 0 ? (
            <div className="p-12 text-center text-muted-foreground">No business rules configured yet.</div>
          ) : (
            <table className="w-full text-left text-xs border-collapse">
              <thead className="bg-muted/60 border-b border-border text-muted-foreground select-none">
                <tr>
                  <th className="p-4 font-semibold uppercase tracking-wider">Rule Name & Target</th>
                  <th className="p-4 font-semibold uppercase tracking-wider">Threshold Condition</th>
                  <th className="p-4 font-semibold uppercase tracking-wider">Severity Level</th>
                  <th className="p-4 font-semibold uppercase tracking-wider">Notification Route</th>
                  <th className="p-4 font-semibold uppercase tracking-wider">Active State</th>
                  <th className="p-4 font-semibold uppercase tracking-wider text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border bg-card">
                {rules.map((r) => (
                  <tr key={r.id} className="hover:bg-muted/20 transition-colors">
                    <td className="p-4 space-y-0.5">
                      <span className="font-bold text-sm text-foreground block">{r.name}</span>
                      <span className="text-[11px] font-mono text-primary">Metric: {r.targetMetric}</span>
                    </td>
                    <td className="p-4 font-mono font-bold text-foreground">
                      {r.condition.replace('_', ' ')} {r.thresholdValue}
                    </td>
                    <td className="p-4">
                      {r.severity === 'CRITICAL' && <Badge variant="danger">Critical</Badge>}
                      {r.severity === 'WARNING' && <Badge variant="warning">Warning</Badge>}
                      {r.severity === 'INFO' && <Badge variant="info">Info</Badge>}
                    </td>
                    <td className="p-4 text-muted-foreground">{r.notificationDestination}</td>
                    <td className="p-4">
                      <button
                        onClick={() => toggleRuleActive(r.id, r.isActive)}
                        className={`px-3 py-1 rounded-full text-xs font-bold transition-colors ${
                          r.isActive
                            ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20'
                            : 'bg-muted text-muted-foreground border border-border'
                        }`}
                      >
                        {r.isActive ? 'Active' : 'Paused'}
                      </button>
                    </td>
                    <td className="p-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => deleteRule(r.id)}
                          className="p-1.5 rounded text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors"
                          title="Delete Rule"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </CardContent>
      </Card>

      {/* Triggered Incidents History */}
      <Card>
        <CardHeader className="pb-3 border-b border-border">
          <CardTitle className="text-base">Recent Triggered Incidents & Audit Log</CardTitle>
          <CardDescription>Historical record of alert dispatches over the last 7 days</CardDescription>
        </CardHeader>
        <CardContent className="p-4 space-y-3">
          {[
            { rule: 'Low Inventory Alert - Wireless Headphones', time: 'Today at 08:14 AM', details: 'SKU-8842 inventory count dropped to 42 units (Threshold: < 50). Email sent to procurement team.', sev: 'WARNING' },
            { rule: 'High Margin Anomaly Alert', time: 'Yesterday at 03:45 PM', details: 'Order ORD-9481 net profit margin reached 48.5% (Threshold: > 45%). Flaged for review.', sev: 'INFO' },
          ].map((inc, i) => (
            <div key={i} className="flex items-start justify-between p-3.5 rounded-xl border border-border bg-card">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <h4 className="text-sm font-bold text-foreground">{inc.rule}</h4>
                  <Badge variant={inc.sev === 'WARNING' ? 'warning' : 'info'} size="sm">{inc.sev}</Badge>
                </div>
                <p className="text-xs text-muted-foreground">{inc.details}</p>
                <span className="text-[11px] font-mono text-muted-foreground block">{inc.time}</span>
              </div>
              <Badge variant="outline" size="sm">Resolved</Badge>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Create Rule Modal */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Create New Business Rule" description="Set up an automated threshold alert for any database metric." size="md">
        <form onSubmit={handleCreateRule} className="space-y-4">
          <Input label="Rule Display Name" placeholder="e.g. Low Stock Warning" value={name} onChange={(e) => setName(e.target.value)} required />
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Select label="Target Metric / Column" value={targetMetric} onChange={(e) => setTargetMetric(e.target.value)}>
              <option value="inventory_count">Inventory Count (Qty)</option>
              <option value="total_amount">Order Gross Amount ($)</option>
              <option value="net_profit">Net Profit ($)</option>
              <option value="discount_code">Discount Application %</option>
            </Select>
            <Select label="Condition" value={condition} onChange={(e) => setCondition(e.target.value as BusinessRule['condition'])}>
              <option value="LESS_THAN">Less Than (&lt;)</option>
              <option value="GREATER_THAN">Greater Than (&gt;)</option>
              <option value="EQUALS">Equals (=)</option>
              <option value="OUTSIDE_RANGE">Outside Range</option>
            </Select>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input label="Threshold Value" type="number" placeholder="50" value={threshold} onChange={(e) => setThreshold(e.target.value)} required />
            <Select label="Severity Level" value={severity} onChange={(e) => setSeverity(e.target.value as BusinessRule['severity'])}>
              <option value="INFO">Info (Log Only)</option>
              <option value="WARNING">Warning (In-App Toast)</option>
              <option value="CRITICAL">Critical (Email & Alert)</option>
            </Select>
          </div>

          <div className="flex justify-end gap-2 pt-4 border-t border-border">
            <Button type="button" variant="ghost" onClick={() => setIsModalOpen(false)}>Cancel</Button>
            <Button type="submit" variant="primary" leftIcon={<Plus className="w-4 h-4" />}>Save & Activate Rule</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
