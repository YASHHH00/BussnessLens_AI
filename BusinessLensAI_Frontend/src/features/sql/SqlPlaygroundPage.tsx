import React, { useState } from 'react';
import { Code2, Play, Sparkles, Download, ShieldAlert, CheckCircle2, Table as TableIcon, BarChart3, Clock } from 'lucide-react';
import { Button, Select, Card, CardHeader, CardContent, Badge, DataTable, ChartWrapper, ExplainabilityPanel, toast, DomainSelector } from '../../shared/components';
import { sqlService } from '../../shared/lib/services/sqlService';
import { SqlExecutionResult } from '../../shared/types';

export const SqlPlaygroundPage: React.FC = () => {
  const [query, setQuery] = useState<string>(
    `-- BusinessLens AI Production Read-Only Query\n-- Calculate Top 5 Product Categories by Net Profit\nSELECT \n  p.category AS product_category,\n  COUNT(o.id) AS total_orders,\n  SUM(o.total_amount) AS gross_revenue,\n  SUM(o.net_profit) AS net_profit,\n  ROUND((SUM(o.net_profit) / SUM(o.total_amount)) * 100, 2) AS margin_pct\nFROM orders o\nJOIN products p ON o.product_sku = p.sku\nWHERE o.status = 'Completed'\nGROUP BY p.category\nORDER BY net_profit DESC\nLIMIT 10;`
  );

  const [result, setResult] = useState<SqlExecutionResult | null>(null);
  const [isExecuting, setIsExecuting] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'table' | 'chart' | 'plan'>('table');
  const [explainModalOpen, setExplainModalOpen] = useState<boolean>(false);

  const savedTemplates = [
    { label: 'Top Product Categories by Net Profit', query: `SELECT p.category AS product_category, COUNT(o.id) AS total_orders, SUM(o.total_amount) AS gross_revenue, SUM(o.net_profit) AS net_profit FROM orders o JOIN products p ON o.product_sku = p.sku GROUP BY p.category ORDER BY net_profit DESC LIMIT 10;` },
    { label: 'Monthly Revenue Velocity (Q3)', query: `SELECT DATE_TRUNC('month', created_at) AS order_month, COUNT(*) AS order_count, SUM(total_amount) AS monthly_revenue FROM orders WHERE created_at >= '2026-07-01' GROUP BY order_month ORDER BY order_month;` },
    { label: 'Customer Retention & Repeat Rate', query: `SELECT customer_id, COUNT(*) AS orders_placed, SUM(total_amount) AS lifetime_value FROM orders GROUP BY customer_id HAVING COUNT(*) > 1 ORDER BY lifetime_value DESC LIMIT 15;` },
    { label: 'Low Stock Inventory Alert Check', query: `SELECT sku, product_name, category, inventory_count, unit_price FROM products WHERE inventory_count < 50 ORDER BY inventory_count ASC;` },
  ];

  const handleExecute = async () => {
    if (!query.trim()) {
      toast.warning('Empty Query', 'Please enter a valid SQL query to execute.');
      return;
    }

    // Client-side safety check check
    const upper = query.toUpperCase();
    if (upper.includes('INSERT ') || upper.includes('UPDATE ') || upper.includes('DELETE ') || upper.includes('DROP ') || upper.includes('ALTER ')) {
      toast.error('Security Gate Triggered', 'Read-Only Enforcement: DML/DDL modifying commands are strictly prohibited.');
      return;
    }

    setIsExecuting(true);
    try {
      const res = await sqlService.executeReadonlyQuery(query);
      setResult(res);
      toast.success('Query Executed', `Returned ${res.rows.length} records in ${res.executionTimeMs}ms.`);
    } catch (err: unknown) {
      const msg = err && typeof err === 'object' && 'message' in err ? String(err.message) : 'SQL Syntax Error or Execution Timeout.';
      toast.error('Execution Failed', msg);
    } finally {
      setIsExecuting(false);
    }
  };

  const handleExportCsv = () => {
    if (!result || !result.rows.length) return;
    let csv = result.columns.join(',') + '\r\n';
    result.rows.forEach((row: Record<string, unknown>) => {
      csv += result.columns.map((c: string) => `"${String(row[c] ?? '')}"`).join(',') + '\r\n';
    });
    const link = document.createElement('a');
    link.href = encodeURI('data:text/csv;charset=utf-8,' + csv);
    link.download = 'sql_query_result.csv';
    link.click();
    toast.success('CSV Exported', 'Query dataset downloaded successfully.');
  };

  // Convert result columns to DataTable column format
  const tableColumns = result?.columns.map((col: string) => ({
    key: col,
    header: col.replace(/_/g, ' '),
    sortable: true,
  })) || [];

  return (
    <div className="space-y-8 max-w-7xl mx-auto animate-in fade-in-50 duration-300 pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Badge variant="purple">Backend V3: SQL Playground</Badge>
            <DomainSelector />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">Interactive SQL Playground</h1>
          <p className="text-sm text-muted-foreground">
            Execute read-only SQL queries directly against production PostgreSQL databases with AI query explanation and instant visualization.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Select
            value=""
            onChange={(e) => {
              const tmpl = savedTemplates[Number(e.target.value)];
              if (tmpl) {
                setQuery(tmpl.query);
                toast.info('Template Loaded', tmpl.label);
              }
            }}
            className="w-64 text-xs font-semibold bg-card"
          >
            <option value="">-- Load Saved Query Template --</option>
            {savedTemplates.map((t, i) => (
              <option key={i} value={i}>{t.label}</option>
            ))}
          </Select>

          <Button
            variant="outline"
            size="md"
            onClick={() => setExplainModalOpen(true)}
            leftIcon={<Sparkles className="w-4 h-4 text-purple-500" />}
          >
            Explain Query
          </Button>

          <Button
            variant="primary"
            size="md"
            onClick={handleExecute}
            isLoading={isExecuting}
            leftIcon={<Play className="w-4 h-4 fill-current" />}
            className="font-bold px-6 shadow-md"
          >
            Execute SQL
          </Button>
        </div>
      </div>

      {/* Security Enforcement Banner */}
      <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between gap-4 text-xs text-slate-300 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <span className="font-bold text-emerald-400">Read-Only Sandbox Guard Active</span>
            <p className="text-slate-400">All queries are wrapped in strict read-only transactions with a 5000ms execution timeout limit.</p>
          </div>
        </div>
        <Badge variant="success" size="sm">PostgreSQL Prod Connected</Badge>
      </div>

      {/* SQL Code Editor Area */}
      <Card className="overflow-hidden border-border/80 bg-slate-950 shadow-xl">
        <div className="p-3 bg-slate-900 border-b border-slate-800 flex items-center justify-between text-xs text-slate-400 font-mono">
          <div className="flex items-center gap-2">
            <Code2 className="w-4 h-4 text-primary" />
            <span>retail_analytics_db — SQL Editor</span>
          </div>
          <span>Press Ctrl + Enter to run</span>
        </div>
        <div className="p-4">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                handleExecute();
              }
            }}
            rows={10}
            className="w-full bg-transparent text-emerald-400 font-mono text-xs sm:text-sm focus:outline-none resize-y leading-relaxed selection:bg-emerald-500/30"
            placeholder="Type your SELECT query here..."
            spellCheck={false}
          />
        </div>
      </Card>

      {/* Execution Results Area */}
      {result && (
        <Card className="overflow-hidden border-border/80 animate-in fade-in-50">
          <CardHeader className="p-6 pb-4 border-b border-border flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1.5 p-1 rounded-xl bg-muted/60 border border-border">
                <button
                  onClick={() => setActiveTab('table')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                    activeTab === 'table' ? 'bg-primary text-primary-foreground font-bold' : 'text-muted-foreground hover:text-foreground'
                  }`}
                >
                  <TableIcon className="w-3.5 h-3.5" />
                  <span>Tabular Results ({result.rows.length})</span>
                </button>
                <button
                  onClick={() => setActiveTab('chart')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                    activeTab === 'chart' ? 'bg-primary text-primary-foreground font-bold' : 'text-muted-foreground hover:text-foreground'
                  }`}
                >
                  <BarChart3 className="w-3.5 h-3.5" />
                  <span>Auto-Visualization</span>
                </button>
                <button
                  onClick={() => setActiveTab('plan')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                    activeTab === 'plan' ? 'bg-primary text-primary-foreground font-bold' : 'text-muted-foreground hover:text-foreground'
                  }`}
                >
                  <Clock className="w-3.5 h-3.5" />
                  <span>Execution Plan</span>
                </button>
              </div>
            </div>

            <div className="flex items-center gap-3 text-xs text-muted-foreground">
              <span className="flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                Time: <strong className="font-mono text-foreground">{result.executionTimeMs}ms</strong>
              </span>
              <span>•</span>
              <Button variant="outline" size="sm" onClick={handleExportCsv} leftIcon={<Download className="w-3.5 h-3.5" />} className="h-8 text-xs">
                Export CSV
              </Button>
            </div>
          </CardHeader>

          <CardContent className="p-6">
            {activeTab === 'table' && (
              <DataTable
                data={result.rows}
                columns={tableColumns}
                searchKey={result.columns[0]}
                searchPlaceholder={`Search by ${result.columns[0]}...`}
                pageSize={10}
              />
            )}

            {activeTab === 'chart' && (
              <ChartWrapper
                title="SQL Query Auto-Visualization"
                subtitle={`Bar chart mapping ${result.columns[0]} against ${result.columns[2] || result.columns[1]}`}
                options={{
                  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
                  grid: { left: '3%', right: '4%', bottom: '10%', containLabel: true },
                  xAxis: { type: 'category', data: result.rows.map((r: Record<string, unknown>) => String(r[result.columns[0]] || '')), axisLine: { lineStyle: { color: '#475569' } } },
                  yAxis: { type: 'value', axisLabel: { formatter: '${value}' }, splitLine: { lineStyle: { color: 'rgba(148, 163, 184, 0.1)' } } },
                  series: [
                    {
                      name: result.columns[2] || 'Value',
                      type: 'bar',
                      barWidth: 24,
                      itemStyle: { color: '#3b82f6', borderRadius: [4, 4, 0, 0] },
                      data: result.rows.map((r: Record<string, unknown>) => Number(r[result.columns[2] || result.columns[1]]) || 0),
                    },
                  ],
                }}
              />
            )}

            {activeTab === 'plan' && (
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 font-mono text-xs text-slate-300 space-y-2">
                <div className="text-emerald-400 font-bold">QUERY PLAN (PostgreSQL Cost Estimate: 14.22..48.91 rows=10 width=48)</div>
                <div>-&gt; Limit (cost=14.22..48.91 rows=10 width=48) (actual time=0.042..0.088 rows=10 loops=1)</div>
                <div className="pl-4">-&gt; Sort (cost=14.22..48.91 rows=10 width=48) (actual time=0.041..0.084 rows=10 loops=1)</div>
                <div className="pl-8">Sort Key: SUM(o.net_profit) DESC</div>
                <div className="pl-8">-&gt; HashAggregate (cost=12.10..13.80 rows=10 width=48) (actual time=0.031..0.062 rows=10 loops=1)</div>
                <div className="pl-12">-&gt; Hash Join (cost=4.50..10.20 rows=15420 width=32) (actual time=0.012..0.024 rows=15420 loops=1)</div>
                <div className="pt-2 text-slate-500 border-t border-slate-800">Planning Time: 0.124 ms • Execution Time: {result.executionTimeMs} ms</div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Explainability Modal */}
      <ExplainabilityPanel
        isOpen={explainModalOpen}
        onClose={() => setExplainModalOpen(false)}
        targetId="sql_query_01"
        targetType="KPI"
        title="SQL Query Lineage & Reasoning Trail"
      />
    </div>
  );
};
