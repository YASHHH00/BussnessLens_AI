import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, BarChart3, TrendingUp, ShoppingBag, Box, Check, ArrowRight, Layers, ShieldCheck, HelpCircle, CheckCircle2 } from 'lucide-react';
import { Button, Card, CardHeader, CardTitle, CardDescription, CardContent, Badge, toast, LoadingState, DomainSelector } from '../../shared/components';
import { dashboardService } from '../../shared/lib/services/dashboardService';
import { RecommendedDashboard } from '../../shared/types';
import { useAppStore } from '../../shared/stores/useAppStore';

export const RecommendationsPage: React.FC = () => {
  const navigate = useNavigate();
  const setWorkflowStep = useAppStore((s) => s.setWorkflowStep);

  const [recommendations, setRecommendations] = useState<RecommendedDashboard[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);

  // Suggested KPIs list
  const [selectedKpis, setSelectedKpis] = useState<Record<string, boolean>>({
    revenue: true,
    margin: true,
    retention: true,
    turnover: true,
    aov: true,
  });

  useEffect(() => {
    setIsLoading(true);
    dashboardService
      .getRecommendedDashboards('conn_pg_01')
      .then((data) => {
        setRecommendations(data);
        setSelectedIds(data.map((d) => d.id)); // Select all by default
        setIsLoading(false);
      })
      .catch(() => setIsLoading(false));
  }, []);

  const toggleDashboard = (id: string) => {
    setSelectedIds((prev) => (prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]));
  };

  const toggleKpi = (key: string) => {
    setSelectedKpis((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const onGenerateSelected = async () => {
    if (selectedIds.length === 0) {
      toast.warning('No Dashboards Selected', 'Please select at least one dashboard layout to generate.');
      return;
    }
    setIsGenerating(true);
    try {
      await dashboardService.generateDashboards(selectedIds);
      toast.success('Dashboards Generated', `${selectedIds.length} tailored dashboards created and cached in Redis!`);
      setWorkflowStep('DASHBOARD_GEN');
      navigate('/dashboards/executive');
    } catch {
      toast.error('Generation Failed', 'Could not generate dashboards.');
    } finally {
      setIsGenerating(false);
    }
  };

  const onGenerateAll = async () => {
    const allIds = recommendations.map((r) => r.id);
    setSelectedIds(allIds);
    setIsGenerating(true);
    try {
      await dashboardService.generateDashboards(allIds);
      toast.success('All Dashboards Generated', '4 comprehensive enterprise dashboards created successfully!');
      setWorkflowStep('DASHBOARD_GEN');
      navigate('/dashboards/executive');
    } catch {
      toast.error('Generation Failed', 'Could not generate dashboards.');
    } finally {
      setIsGenerating(false);
    }
  };

  const kpisList = [
    { key: 'revenue', title: 'Total Gross Revenue', desc: 'SUM(orders.total_amount)', conf: 99 },
    { key: 'margin', title: 'Net Profit Margin %', desc: 'SUM(net_profit) / SUM(total_amount)', conf: 98 },
    { key: 'retention', title: 'Customer Retention Rate', desc: 'Repeat orders / Total customers', conf: 94 },
    { key: 'turnover', title: 'Inventory Turnover Velocity', desc: 'COGS / Average Inventory Count', conf: 91 },
    { key: 'aov', title: 'Average Order Value (AOV)', desc: 'SUM(total_amount) / COUNT(orders)', conf: 97 },
  ];

  const getIconForCategory = (cat: string) => {
    switch (cat) {
      case 'EXECUTIVE':
        return <BarChart3 className="w-5 h-5 text-primary" />;
      case 'SALES':
        return <ShoppingBag className="w-5 h-5 text-purple-500" />;
      case 'INVENTORY':
        return <Box className="w-5 h-5 text-blue-500" />;
      case 'FORECAST':
        return <TrendingUp className="w-5 h-5 text-emerald-500" />;
      default:
        return <BarChart3 className="w-5 h-5 text-primary" />;
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto animate-in fade-in-50 duration-300 pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Badge variant="purple">Step 6: Dashboard Recommendations</Badge>
            <DomainSelector />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">AI Recommended Dashboards & KPIs</h1>
          <p className="text-sm text-muted-foreground">
            Based on your PostgreSQL retail schema and confirmed semantic mappings, our AI recommends generating these tailored layouts.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button variant="outline" size="md" onClick={() => navigate('/dashboards/executive')}>
            Skip to Dashboards
          </Button>
          <Button
            variant="primary"
            size="md"
            onClick={onGenerateSelected}
            isLoading={isGenerating}
            rightIcon={<ArrowRight className="w-4 h-4" />}
          >
            Generate Selected ({selectedIds.length})
          </Button>
        </div>
      </div>

      {/* Top Banner */}
      <Card className="border-primary/30 bg-gradient-to-r from-card via-card to-purple-500/10">
        <CardContent className="p-6 flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-2xl bg-purple-500/10 text-purple-500 shadow-inner">
              <Sparkles className="w-8 h-8 animate-pulse" />
            </div>
            <div className="space-y-1">
              <h3 className="text-lg font-bold text-foreground">AI Synthesis: Retail Domain Blueprint Ready</h3>
              <p className="text-xs text-muted-foreground max-w-xl leading-relaxed">
                The recommendation engine has analyzed 15,420 transaction records and identified 5 high-impact KPIs and 4 domain-specific dashboard layouts tailored for Executive and Analytical roles.
              </p>
            </div>
          </div>
          <Button variant="outline" size="md" onClick={onGenerateAll} leftIcon={<CheckCircle2 className="w-4 h-4 text-emerald-500" />}>
            Generate All Recommended (4)
          </Button>
        </CardContent>
      </Card>

      {/* Suggested KPIs Selection */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold tracking-tight text-foreground flex items-center gap-2">
            <Layers className="w-5 h-5 text-primary" />
            <span>Suggested Domain KPIs</span>
          </h2>
          <span className="text-xs text-muted-foreground">Select key performance indicators to include in top metric cards</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          {kpisList.map((kpi) => {
            const isChecked = !!selectedKpis[kpi.key];
            return (
              <Card
                key={kpi.key}
                onClick={() => toggleKpi(kpi.key)}
                className={`cursor-pointer transition-all border-2 ${
                  isChecked ? 'border-primary bg-primary/5 shadow-sm' : 'border-border/60 bg-card hover:bg-muted/40 opacity-70'
                }`}
              >
                <CardContent className="p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <input
                      type="checkbox"
                      checked={isChecked}
                      onChange={() => {}}
                      className="w-4 h-4 rounded text-primary focus:ring-primary border-input bg-background"
                    />
                    <Badge variant="success" size="sm">{kpi.conf}% Conf</Badge>
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-foreground">{kpi.title}</h4>
                    <span className="text-[11px] font-mono text-muted-foreground block mt-0.5 truncate" title={kpi.desc}>
                      {kpi.desc}
                    </span>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Recommended Dashboards Grid */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold tracking-tight text-foreground flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-purple-500" />
            <span>Recommended Dashboard Layouts</span>
          </h2>
          <span className="text-xs text-muted-foreground">Click any card to select or deselect for generation</span>
        </div>

        {isLoading ? (
          <LoadingState type="card" count={4} message="Analyzing schema to generate recommendations..." />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {recommendations.map((dash) => {
              const isSelected = selectedIds.includes(dash.id);

              return (
                <Card
                  key={dash.id}
                  onClick={() => toggleDashboard(dash.id)}
                  className={`cursor-pointer transition-all duration-200 border-2 flex flex-col justify-between ${
                    isSelected ? 'border-primary bg-primary/[0.03] shadow-md scale-[1.01]' : 'border-border bg-card hover:border-primary/40 opacity-80'
                  }`}
                >
                  <CardHeader className="pb-4 border-b border-border">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex items-center gap-3">
                        <div className="p-2.5 rounded-xl bg-muted">{getIconForCategory(dash.category)}</div>
                        <div>
                          <div className="flex items-center gap-2">
                            <CardTitle className="text-base font-bold text-foreground">{dash.title}</CardTitle>
                            <Badge variant="outline" size="sm">{dash.category}</Badge>
                          </div>
                          <span className="text-xs text-muted-foreground">{dash.widgetCount} Visual Widgets</span>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        <Badge variant="success" size="sm">{dash.confidence}% Conf</Badge>
                        <div
                          className={`w-6 h-6 rounded-full flex items-center justify-center border transition-colors ${
                            isSelected ? 'bg-primary border-primary text-primary-foreground' : 'border-border bg-card text-transparent'
                          }`}
                        >
                          <Check className="w-3.5 h-3.5 stroke-[3]" />
                        </div>
                      </div>
                    </div>
                    <CardDescription className="pt-2 leading-relaxed">{dash.description}</CardDescription>
                  </CardHeader>

                  <CardContent className="p-6 space-y-4">
                    <div className="space-y-2">
                      <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground block">
                        Included Visualizations & Metrics:
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {dash.suggestedWidgets?.map((w: string, idx: number) => (
                          <Badge key={idx} variant="outline" className="text-xs bg-background">
                            {w}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    <div className="pt-3 border-t border-border flex items-center justify-between text-xs text-muted-foreground">
                      <span>Target Role: <strong className="text-foreground">{dash.category === 'EXECUTIVE' ? 'Executive Leadership' : 'Business Managers & Analysts'}</strong></span>
                      <span className="text-primary font-bold">{isSelected ? 'Selected for Generation' : 'Click to Select'}</span>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </div>

      {/* Bottom CTA */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-card to-primary/10 border border-border flex flex-col sm:flex-row items-center justify-between gap-4 shadow-sm">
        <div className="space-y-1">
          <h3 className="text-base font-bold text-foreground flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-500" />
            <span>Ready to Build Your BI Workspace</span>
          </h3>
          <p className="text-xs text-muted-foreground">
            Generate your selected dashboards now. All layouts are fully customizable in our drag-and-drop builder!
          </p>
        </div>
        <Button
          variant="primary"
          size="lg"
          onClick={onGenerateSelected}
          isLoading={isGenerating}
          rightIcon={<ArrowRight className="w-4 h-4" />}
          className="w-full sm:w-auto font-bold"
        >
          Generate {selectedIds.length} Dashboards & Open Workspace
        </Button>
      </div>
    </div>
  );
};
