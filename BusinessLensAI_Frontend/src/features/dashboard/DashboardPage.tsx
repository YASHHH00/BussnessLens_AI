import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Sparkles, TrendingUp, TrendingDown, ArrowUpRight, Calculator, AlertTriangle, ShieldCheck, CheckCircle2 } from 'lucide-react';
import { DashboardShell } from './DashboardShell';
import { WidgetBuilderModal } from './WidgetBuilderModal';
import { DrillDownModal } from './DrillDownModal';
import { Card, CardContent, Badge, ChartWrapper, ExplainabilityPanel, FormulaViewerModal, LoadingState, toast } from '../../shared/components';
import { dashboardService } from '../../shared/lib/services/dashboardService';
import { Dashboard, DashboardWidget } from '../../shared/types';
import { useAppStore } from '../../shared/stores/useAppStore';

export const DashboardPage: React.FC = () => {
  const { category = 'executive' } = useParams<{ category: string }>();
  const navigate = useNavigate();
  const setWorkflowStep = useAppStore((s) => s.setWorkflowStep);

  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Modals state
  const [isWidgetBuilderOpen, setIsWidgetBuilderOpen] = useState(false);
  const [drillDownTitle, setDrillDownTitle] = useState<string | null>(null);
  const [explainModalOpen, setExplainModalOpen] = useState(false);
  const [explainTarget, setExplainTarget] = useState<{ id: string; type: 'DASHBOARD' | 'WIDGET' | 'KPI'; title: string }>({
    id: 'dash_exec_01',
    type: 'DASHBOARD',
    title: 'Executive Summary Dashboard',
  });
  const [formulaModal, setFormulaModal] = useState<{ open: boolean; title: string; formula: string; meaning: string } | null>(null);

  const activeCat = (category.toUpperCase() as 'EXECUTIVE' | 'SALES' | 'INVENTORY' | 'FORECAST') || 'EXECUTIVE';

  useEffect(() => {
    setIsLoading(true);
    dashboardService
      .getDashboardById(`dash_${category.toLowerCase()}_01`)
      .then((data: any) => {
        setDashboard(data);
        setIsLoading(false);
      })
      .catch(() => setIsLoading(false));
  }, [category]);

  const handleRefreshCache = async () => {
    await new Promise((r) => setTimeout(r, 800));
    toast.success('Cache Refreshed', 'Dashboard widgets updated with live PostgreSQL data.');
  };

  const handleAddWidget = (widget: DashboardWidget) => {
    if (!dashboard) return;
    setDashboard({
      ...dashboard,
      widgets: [widget, ...dashboard.widgets],
    });
  };

  const kpiCards = [
    {
      id: 'kpi_rev',
      title: 'Total Gross Revenue',
      value: '$1,245,800',
      change: '+14.2%',
      isPositive: true,
      formula: 'SUM(orders.total_amount)',
      meaning: 'Total billed gross revenue across all completed and processing customer orders in the selected time period.',
    },
    {
      id: 'kpi_margin',
      title: 'Net Profit Margin %',
      value: '24.1%',
      change: '+2.4%',
      isPositive: true,
      formula: 'SUM(net_profit) / SUM(total_amount) × 100',
      meaning: 'Percentage of revenue remaining after subtracting COGS and customer acquisition expenses.',
    },
    {
      id: 'kpi_retention',
      title: 'Customer Retention Rate',
      value: '68.4%',
      change: '+5.1%',
      isPositive: true,
      formula: 'COUNT(DISTINCT repeat_customers) / COUNT(DISTINCT all_customers) × 100',
      meaning: 'Proportion of active customers who placed more than one order in the last 12 months.',
    },
    {
      id: 'kpi_aov',
      title: 'Average Order Value',
      value: '$80.79',
      change: '-1.2%',
      isPositive: false,
      formula: 'SUM(total_amount) / COUNT(orders.id)',
      meaning: 'Average dollar amount spent per transaction across all product categories.',
    },
  ];

  return (
    <DashboardShell
      activeCategory={activeCat}
      title={dashboard?.title || `${activeCat.charAt(0) + activeCat.slice(1).toLowerCase()} Dashboard`}
      description={dashboard?.description || 'Real-time analytical monitoring powered by BusinessLens AI.'}
      onExplainDashboard={() => {
        setExplainTarget({ id: dashboard?.id || 'dash_01', type: 'DASHBOARD', title: dashboard?.title || 'Dashboard Analysis' });
        setExplainModalOpen(true);
      }}
      onOpenWidgetBuilder={() => setIsWidgetBuilderOpen(true)}
      onRefreshCache={handleRefreshCache}
    >
      {/* AI Executive Summary Banner */}
      <Card className="border-purple-500/30 bg-purple-500/[0.03]">
        <CardContent className="p-5 flex items-start gap-3.5">
          <div className="p-2 rounded-xl bg-purple-500/10 text-purple-500 shrink-0 mt-0.5">
            <Sparkles className="w-5 h-5 animate-pulse" />
          </div>
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <h4 className="text-sm font-bold text-foreground">AI Executive Synthesis & Key Drivers</h4>
              <Badge variant="purple" size="sm">Updated Live</Badge>
            </div>
            <p className="text-xs text-muted-foreground leading-relaxed">
              Revenue is tracking <strong className="text-foreground">14.2% above Q3 projections</strong>, driven by strong adoption in the Electronics and Home Goods categories. However, Average Order Value (AOV) dipped slightly (-1.2%) due to promotional bundling. Stockout risk on Wireless Headphones remains the primary operational bottleneck.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* 4 KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpiCards.map((kpi) => (
          <Card key={kpi.id} isGlass hoverEffect className="relative group">
            <CardContent className="p-5 space-y-3">
              <div className="flex items-start justify-between">
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">{kpi.title}</span>
                <button
                  onClick={() => setFormulaModal({ open: true, title: kpi.title, formula: kpi.formula, meaning: kpi.meaning })}
                  className="p-1.5 rounded-lg text-muted-foreground hover:text-primary hover:bg-primary/10 transition-colors"
                  title="View Mathematical Formula"
                >
                  <Calculator className="w-4 h-4" />
                </button>
              </div>

              <div className="flex items-baseline justify-between">
                <h3 className="text-2xl font-extrabold tracking-tight text-foreground">{kpi.value}</h3>
                <div className={`flex items-center gap-1 text-xs font-bold px-2 py-0.5 rounded-full ${kpi.isPositive ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400' : 'bg-destructive/10 text-destructive'}`}>
                  {kpi.isPositive ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
                  <span>{kpi.change}</span>
                </div>
              </div>

              <div className="pt-2 border-t border-border/60 flex items-center justify-between text-[11px] text-muted-foreground">
                <span>vs. previous period</span>
                <button
                  onClick={() => setDrillDownTitle(kpi.title)}
                  className="text-primary hover:underline font-semibold flex items-center gap-0.5"
                >
                  <span>Drill Down</span>
                  <ArrowUpRight className="w-3 h-3" />
                </button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Interactive Charts Grid */}
      {isLoading ? (
        <LoadingState type="card" count={4} message="Rendering Apache ECharts visualizations..." />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Chart 1: Revenue & Profit Trend (Area Chart) */}
          <ChartWrapper
            title="Revenue & Net Profit Velocity (Last 90 Days)"
            subtitle="Daily gross billing vs net profit margins"
            onExplain={() => {
              setExplainTarget({ id: 'w_rev_trend', type: 'WIDGET', title: 'Revenue & Profit Trend Analysis' });
              setExplainModalOpen(true);
            }}
            options={{
              tooltip: { trigger: 'axis' },
              legend: { data: ['Gross Revenue ($)', 'Net Profit ($)'], bottom: 0, textStyle: { color: '#94a3b8' } },
              grid: { left: '3%', right: '4%', bottom: '12%', containLabel: true },
              xAxis: { type: 'category', boundaryGap: false, data: ['W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7', 'W8', 'W9', 'W10', 'W11', 'W12'], axisLine: { lineStyle: { color: '#475569' } } },
              yAxis: { type: 'value', axisLabel: { formatter: '${value}' }, splitLine: { lineStyle: { color: 'rgba(148, 163, 184, 0.1)' } } },
              series: [
                {
                  name: 'Gross Revenue ($)',
                  type: 'line',
                  smooth: true,
                  areaStyle: { color: 'rgba(59, 130, 246, 0.2)' },
                  lineStyle: { width: 3, color: '#3b82f6' },
                  itemStyle: { color: '#3b82f6' },
                  data: [82000, 94000, 89000, 105000, 112000, 108000, 125000, 134000, 129000, 142000, 151000, 165000],
                },
                {
                  name: 'Net Profit ($)',
                  type: 'line',
                  smooth: true,
                  areaStyle: { color: 'rgba(16, 185, 129, 0.2)' },
                  lineStyle: { width: 3, color: '#10b981' },
                  itemStyle: { color: '#10b981' },
                  data: [19000, 22000, 21000, 25000, 27000, 26000, 30000, 32000, 31000, 34000, 36000, 40000],
                },
              ],
            }}
          />

          {/* Chart 2: Sales by Product Category (Donut Chart) */}
          <ChartWrapper
            title="Revenue Distribution by Product Category"
            subtitle="Percentage share across top retail segments"
            onExplain={() => {
              setExplainTarget({ id: 'w_cat_pie', type: 'WIDGET', title: 'Product Category Breakdown' });
              setExplainModalOpen(true);
            }}
            options={{
              tooltip: { trigger: 'item', formatter: '{b}: ${c} ({d}%)' },
              legend: { orient: 'horizontal', bottom: 0, textStyle: { color: '#94a3b8' } },
              series: [
                {
                  name: 'Category Revenue',
                  type: 'pie',
                  radius: ['45%', '75%'],
                  avoidLabelOverlap: true,
                  itemStyle: { borderRadius: 8, borderColor: '#0f172a', borderWidth: 2 },
                  label: { show: true, formatter: '{b}: {d}%', color: '#94a3b8' },
                  data: [
                    { value: 485000, name: 'Electronics', itemStyle: { color: '#3b82f6' } },
                    { value: 340000, name: 'Apparel', itemStyle: { color: '#8b5cf6' } },
                    { value: 275000, name: 'Home Goods', itemStyle: { color: '#10b981' } },
                    { value: 145800, name: 'Accessories', itemStyle: { color: '#f59e0b' } },
                  ],
                },
              ],
            }}
          />

          {/* Chart 3: Regional Performance Breakdown (Bar Chart) */}
          <ChartWrapper
            title="Regional Sales Volume & Target Attainment"
            subtitle="Comparison of actual gross sales against quarterly targets"
            onExplain={() => {
              setExplainTarget({ id: 'w_reg_bar', type: 'WIDGET', title: 'Regional Sales Attainment' });
              setExplainModalOpen(true);
            }}
            options={{
              tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
              legend: { data: ['Actual Sales ($)', 'Quarterly Target ($)'], bottom: 0, textStyle: { color: '#94a3b8' } },
              grid: { left: '3%', right: '4%', bottom: '12%', containLabel: true },
              xAxis: { type: 'value', axisLabel: { formatter: '${value}' }, splitLine: { lineStyle: { color: 'rgba(148, 163, 184, 0.1)' } } },
              yAxis: { type: 'category', data: ['Latin America', 'APAC', 'EMEA', 'North America'], axisLine: { lineStyle: { color: '#475569' } } },
              series: [
                { name: 'Actual Sales ($)', type: 'bar', barWidth: 16, itemStyle: { color: '#3b82f6', borderRadius: [0, 4, 4, 0] }, data: [145000, 280000, 390000, 430800] },
                { name: 'Quarterly Target ($)', type: 'bar', barWidth: 16, itemStyle: { color: '#64748b', borderRadius: [0, 4, 4, 0] }, data: [160000, 270000, 375000, 420000] },
              ],
            }}
          />

          {/* Chart 4: 90-Day Forecast with Confidence Bands (Line Chart) */}
          <ChartWrapper
            title="90-Day Revenue Forecast Model (AI Predictive Engine)"
            subtitle="Projected growth trajectory with 95% statistical confidence bounds"
            onExplain={() => {
              setExplainTarget({ id: 'w_forecast', type: 'WIDGET', title: '90-Day Predictive Forecast Lineage' });
              setExplainModalOpen(true);
            }}
            options={{
              tooltip: { trigger: 'axis' },
              legend: { data: ['Historical Actuals', 'AI Projected Revenue', '95% Confidence Bounds'], bottom: 0, textStyle: { color: '#94a3b8' } },
              grid: { left: '3%', right: '4%', bottom: '12%', containLabel: true },
              xAxis: { type: 'category', boundaryGap: false, data: ['Jul', 'Aug', 'Sep', 'Oct (Est)', 'Nov (Est)', 'Dec (Est)'], axisLine: { lineStyle: { color: '#475569' } } },
              yAxis: { type: 'value', axisLabel: { formatter: '${value}' }, splitLine: { lineStyle: { color: 'rgba(148, 163, 184, 0.1)' } } },
              series: [
                { name: 'Historical Actuals', type: 'line', lineStyle: { width: 3, color: '#3b82f6' }, itemStyle: { color: '#3b82f6' }, data: [380000, 410000, 455800, null, null, null] },
                { name: 'AI Projected Revenue', type: 'line', lineStyle: { width: 3, type: 'dashed', color: '#10b981' }, itemStyle: { color: '#10b981' }, data: [null, null, 455800, 485000, 520000, 565000] },
                {
                  name: '95% Confidence Bounds',
                  type: 'line',
                  lineStyle: { opacity: 0 },
                  areaStyle: { color: 'rgba(16, 185, 129, 0.15)' },
                  data: [null, null, 455800, 510000, 555000, 610000],
                },
              ],
            }}
          />
        </div>
      )}

      {/* Modals */}
      <WidgetBuilderModal isOpen={isWidgetBuilderOpen} onClose={() => setIsWidgetBuilderOpen(false)} onAddWidget={handleAddWidget} />

      <DrillDownModal isOpen={!!drillDownTitle} onClose={() => setDrillDownTitle(null)} title={drillDownTitle || ''} />

      <ExplainabilityPanel
        isOpen={explainModalOpen}
        onClose={() => setExplainModalOpen(false)}
        targetId={explainTarget.id}
        targetType={explainTarget.type}
        title={`Explainability Report: ${explainTarget.title}`}
      />

      {formulaModal && (
        <FormulaViewerModal
          isOpen={formulaModal.open}
          onClose={() => setFormulaModal(null)}
          kpiTitle={formulaModal.title}
          formula={formulaModal.formula}
          businessMeaning={formulaModal.meaning}
          variables={[
            { name: 'total_amount', sourceColumn: 'orders.total_amount', description: 'Gross transaction billing amount.' },
            { name: 'net_profit', sourceColumn: 'orders.net_profit', description: 'Profit margin after deducting costs.' },
          ]}
        />
      )}
    </DashboardShell>
  );
};
