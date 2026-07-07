import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, RefreshCw, Plus, FileText, History, Filter, Calendar, BarChart3, ShoppingBag, Box, TrendingUp, ShieldCheck } from 'lucide-react';
import { Button, Select, Badge, CacheStatusBadge, AICostTransparencyBadge, Modal, toast, DomainSelector } from '../../shared/components';
import { useAppStore } from '../../shared/stores/useAppStore';

export interface DashboardShellProps {
  activeCategory: 'EXECUTIVE' | 'SALES' | 'INVENTORY' | 'FORECAST';
  title: string;
  description: string;
  onExplainDashboard: () => void;
  onOpenWidgetBuilder: () => void;
  onRefreshCache: () => Promise<void> | void;
  children: React.ReactNode;
}

export const DashboardShell: React.FC<DashboardShellProps> = ({
  activeCategory,
  title,
  description,
  onExplainDashboard,
  onOpenWidgetBuilder,
  onRefreshCache,
  children,
}) => {
  const navigate = useNavigate();
  const dateRange = useAppStore((s) => s.globalDateRange);
  const setDateRange = useAppStore((s) => s.setGlobalDateRange);
  const regionFilter = useAppStore((s) => s.globalRegionFilter);
  const setRegionFilter = useAppStore((s) => s.setGlobalRegionFilter);

  const [isHistoryModalOpen, setIsHistoryModalOpen] = useState(false);
  const [isRegeneratingAi, setIsRegeneratingAi] = useState(false);

  const handleRegenerateAi = async () => {
    setIsRegeneratingAi(true);
    await new Promise((r) => setTimeout(r, 1200));
    setIsRegeneratingAi(false);
    toast.success('AI Insights Regenerated', 'Executive summary and key anomaly drivers have been synthesized from live data.');
  };

  const handleExportReport = () => {
    toast.info('Export Started', 'Compiling multi-page PDF executive presentation...');
    setTimeout(() => {
      toast.success('Report Exported', 'Executive_Dashboard_Q3.pdf downloaded.');
    }, 1500);
  };

  const categories: { id: typeof activeCategory; label: string; icon: React.ReactNode; path: string }[] = [
    { id: 'EXECUTIVE', label: 'Executive Summary', icon: <BarChart3 className="w-4 h-4" />, path: '/dashboards/executive' },
    { id: 'SALES', label: 'Sales & Revenue', icon: <ShoppingBag className="w-4 h-4" />, path: '/dashboards/sales' },
    { id: 'INVENTORY', label: 'Inventory & Stockouts', icon: <Box className="w-4 h-4" />, path: '/dashboards/inventory' },
    { id: 'FORECAST', label: '90-Day AI Forecast', icon: <TrendingUp className="w-4 h-4" />, path: '/dashboards/forecast' },
  ];

  return (
    <div className="space-y-6 animate-in fade-in-50 duration-300">
      {/* Top Header & Category Tabs */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-4 border-b border-border">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Badge variant="purple">Step 7: Dashboards</Badge>
            <DomainSelector />
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-foreground">{title}</h1>
          <p className="text-sm text-muted-foreground">{description}</p>
        </div>

        {/* Category switcher */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-muted/60 border border-border overflow-x-auto">
          {categories.map((cat) => {
            const isActive = activeCategory === cat.id;
            return (
              <button
                key={cat.id}
                onClick={() => navigate(cat.path)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-all ${
                  isActive
                    ? 'bg-primary text-primary-foreground shadow-sm font-bold'
                    : 'text-muted-foreground hover:text-foreground hover:bg-card'
                }`}
              >
                {cat.icon}
                <span>{cat.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Enhanced Toolbar: Filters & Action Buttons */}
      <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4 p-4 rounded-2xl bg-card border border-border shadow-sm">
        {/* Left: Global Date & Dimension Filters */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-muted-foreground">
            <Calendar className="w-4 h-4 text-primary" />
            <span>Period:</span>
          </div>
          <Select value={typeof dateRange === 'string' ? dateRange : '30d'} onChange={(e) => setDateRange(e.target.value as any)} className="w-36 h-8 text-xs py-0">
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days (Q3)</option>
            <option value="ytd">Year to Date (YTD)</option>
            <option value="1y">Full Year (12M)</option>
          </Select>

          <div className="h-4 w-px bg-border hidden sm:block" />

          <div className="flex items-center gap-1.5 text-xs font-semibold text-muted-foreground">
            <Filter className="w-4 h-4 text-blue-500" />
            <span>Region:</span>
          </div>
          <Select value={regionFilter} onChange={(e) => setRegionFilter(e.target.value)} className="w-36 h-8 text-xs py-0">
            <option value="ALL">All Regions (Global)</option>
            <option value="NORTH">North America</option>
            <option value="EUROPE">Europe (EMEA)</option>
            <option value="ASIA">Asia-Pacific (APAC)</option>
            <option value="LATAM">Latin America</option>
          </Select>
        </div>

        {/* Right: Actions */}
        <div className="flex flex-wrap items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={onExplainDashboard}
            leftIcon={<Sparkles className="w-3.5 h-3.5 text-purple-500" />}
            className="h-8 text-xs font-semibold"
          >
            Explain Dashboard
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={handleRegenerateAi}
            isLoading={isRegeneratingAi}
            leftIcon={<RefreshCw className="w-3.5 h-3.5 text-blue-500" />}
            className="h-8 text-xs font-semibold"
          >
            Regenerate AI Summary
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsHistoryModalOpen(true)}
            leftIcon={<History className="w-3.5 h-3.5 text-amber-500" />}
            className="h-8 text-xs font-semibold"
            title="View Dashboard Version History"
          >
            History
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={handleExportReport}
            leftIcon={<FileText className="w-3.5 h-3.5 text-emerald-500" />}
            className="h-8 text-xs font-semibold"
            title="Export Report PDF / Excel"
          >
            Export
          </Button>

          <Button
            variant="primary"
            size="sm"
            onClick={onOpenWidgetBuilder}
            leftIcon={<Plus className="w-3.5 h-3.5" />}
            className="h-8 text-xs font-bold shadow-sm"
          >
            Add Widget
          </Button>
        </div>
      </div>

      {/* Cache status & AI Transparency Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 px-1">
        <CacheStatusBadge
          status={{
            isCached: true,
            statusText: 'LIVE',
            cachedAt: new Date(Date.now() - 1000 * 60 * 10).toISOString(),
            lastUpdated: new Date(Date.now() - 1000 * 60 * 10).toISOString(),
            ttlSeconds: 3600,
          }}
          onRefresh={onRefreshCache}
        />
        <AICostTransparencyBadge source="AI_SUMMARY" />
      </div>

      {/* Main Dashboard Content Area */}
      <div className="space-y-6">{children}</div>

      {/* Version History Modal */}
      <Modal
        isOpen={isHistoryModalOpen}
        onClose={() => setIsHistoryModalOpen(false)}
        title="Dashboard Version Audit Trail"
        description="Review past layout modifications and rollback to previous production versions."
        size="md"
      >
        <div className="space-y-3">
          {[
            { version: 'v3.2 (Active)', date: 'Today at 08:30 AM', user: 'Alex Rivera (Executive)', desc: 'Added 90-Day Forecast Confidence Bands chart.', active: true },
            { version: 'v3.1', date: 'Yesterday at 04:15 PM', user: 'AI Recommendation Engine', desc: 'Auto-generated Executive & Sales layouts from Retail V1 schema.', active: false },
            { version: 'v3.0', date: 'July 01, 2026', user: 'System Admin', desc: 'Initial workspace baseline created.', active: false },
          ].map((ver, idx) => (
            <div key={idx} className={`p-3.5 rounded-xl border flex items-start justify-between ${ver.active ? 'bg-primary/10 border-primary text-foreground font-bold' : 'bg-card border-border text-muted-foreground'}`}>
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-extrabold text-foreground">{ver.version}</span>
                  {ver.active && <Badge variant="success" size="sm">Current Production</Badge>}
                </div>
                <p className="text-xs text-muted-foreground">{ver.desc}</p>
                <span className="text-[11px] font-mono text-muted-foreground block">{ver.date} • by {ver.user}</span>
              </div>
              {!ver.active && (
                <Button variant="outline" size="sm" onClick={() => { toast.success('Version Restored', `Rolled back to ${ver.version}.`); setIsHistoryModalOpen(false); }} className="text-xs h-7">
                  Restore
                </Button>
              )}
            </div>
          ))}
          <div className="flex justify-end pt-2 border-t border-border">
            <Button variant="primary" onClick={() => setIsHistoryModalOpen(false)}>
              Close History
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
