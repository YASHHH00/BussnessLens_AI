import React, { useState } from 'react';
import { FileText, Download, Mail, Calendar, CheckCircle2, ShieldCheck, Layers, Sparkles, Clock, Share2, Table as TableIcon, BarChart3 } from 'lucide-react';
import { Button, Select, Card, CardHeader, CardTitle, CardDescription, CardContent, Badge, toast, DomainSelector } from '../../shared/components';

export const ReportsPage: React.FC = () => {
  const [format, setFormat] = useState<'PDF' | 'EXCEL' | 'PPTX' | 'PNG'>('PDF');
  const [scope, setScope] = useState<'EXECUTIVE' | 'SALES' | 'INVENTORY' | 'FORECAST' | 'FULL'>('EXECUTIVE');
  const [includeAiSummary, setIncludeAiSummary] = useState(true);
  const [includeFormulas, setIncludeFormulas] = useState(true);
  const [includeQualityBadge, setIncludeQualityBadge] = useState(true);
  const [includeAuditStamp, setIncludeAuditStamp] = useState(true);

  // Schedule Delivery State
  const [scheduleFreq, setScheduleFreq] = useState('WEEKLY');
  const [emailRecipients, setEmailRecipients] = useState('executives@businesslens.ai, board@businesslens.ai');
  const [isExporting, setIsExporting] = useState(false);
  const [isScheduling, setIsScheduling] = useState(false);

  const handleExport = async () => {
    setIsExporting(true);
    toast.info('Compiling Report', `Generating ${format} document for ${scope.toLowerCase()} dashboard scope...`);
    await new Promise((r) => setTimeout(r, 2000));
    setIsExporting(false);
    toast.success('Report Exported Successfully', `${scope}_Dashboard_Report_Q3.${format.toLowerCase()} has been downloaded to your system.`);
  };

  const handleSchedule = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsScheduling(true);
    await new Promise((r) => setTimeout(r, 1200));
    setIsScheduling(false);
    toast.success('Automated Schedule Created', `Report will be dispatched ${scheduleFreq.toLowerCase()} to ${emailRecipients.split(',').length} recipients.`);
  };

  const recentExports = [
    { name: 'Executive_Summary_Dashboard_Q3.pdf', date: 'Today at 08:45 AM', by: 'Alex Rivera (Executive)', format: 'PDF', size: '4.2 MB' },
    { name: 'Sales_Revenue_Lineage_Data.xlsx', date: 'Yesterday at 04:12 PM', by: 'Sarah Jenkins (Manager)', format: 'EXCEL', size: '12.8 MB' },
    { name: '90Day_AI_Forecast_Presentation.pptx', date: 'July 03, 2026', by: 'Alex Rivera (Executive)', format: 'PPTX', size: '8.5 MB' },
  ];

  return (
    <div className="space-y-8 max-w-7xl mx-auto animate-in fade-in-50 duration-300 pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Badge variant="purple">Backend V3: Report Exporter</Badge>
            <DomainSelector />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">Report Exporter & Scheduled Delivery</h1>
          <p className="text-sm text-muted-foreground">
            Generate enterprise presentation decks, Excel datasets, and PDF executive briefs with automated email routing.
          </p>
        </div>

        <Button
          variant="primary"
          size="md"
          onClick={handleExport}
          isLoading={isExporting}
          leftIcon={<Download className="w-4 h-4" />}
          className="font-bold px-6 shadow-md"
        >
          Generate & Download {format} Report
        </Button>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Exporter Configuration */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Document Export Configuration</CardTitle>
              <CardDescription>Select file format, target dashboard scope, and embedded compliance trails</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Format selection */}
              <div className="space-y-2">
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider block">1. Select Target File Format:</span>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  {[
                    { id: 'PDF', label: 'PDF Presentation', desc: 'Executive Brief & Charts', icon: <FileText className="w-5 h-5 text-destructive" /> },
                    { id: 'EXCEL', label: 'Excel Workbook', desc: 'Raw Data & Pivot Tables', icon: <TableIcon className="w-5 h-5 text-emerald-500" /> },
                    { id: 'PPTX', label: 'PowerPoint Deck', desc: 'Slide Deck Format', icon: <Share2 className="w-5 h-5 text-amber-500" /> },
                    { id: 'PNG', label: 'High-Res Images', desc: 'PNG / JPEG Visuals', icon: <BarChart3 className="w-5 h-5 text-blue-500" /> },
                  ].map((fmt) => {
                    const isSelected = format === fmt.id;
                    return (
                      <button
                        key={fmt.id}
                        type="button"
                        onClick={() => setFormat(fmt.id as any)}
                        className={`p-4 rounded-xl border-2 text-left transition-all ${
                          isSelected ? 'border-primary bg-primary/5 shadow-sm font-bold' : 'border-border bg-card hover:bg-muted/30'
                        }`}
                      >
                        <div className="flex items-center justify-between pb-2">
                          {fmt.icon}
                          {isSelected && <Badge variant="success" size="sm">Selected</Badge>}
                        </div>
                        <h4 className="text-sm font-bold text-foreground">{fmt.label}</h4>
                        <span className="text-[10px] text-muted-foreground block mt-0.5">{fmt.desc}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Scope selection */}
              <div className="space-y-2">
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider block">2. Select Dashboard Scope:</span>
                <Select value={scope} onChange={(e) => setScope(e.target.value as any)} className="text-xs font-bold">
                  <option value="EXECUTIVE">Executive Summary Dashboard (4 KPI Cards + 4 Visual Widgets)</option>
                  <option value="SALES">Sales & Revenue Breakdown Dashboard</option>
                  <option value="INVENTORY">Inventory Risk & Stockouts Dashboard</option>
                  <option value="FORECAST">90-Day AI Forecast & Confidence Bands Dashboard</option>
                  <option value="FULL">Full Enterprise BI Portfolio (All 4 Dashboards Combined)</option>
                </Select>
              </div>

              {/* Embedded Compliance Checkboxes */}
              <div className="space-y-3 pt-2 border-t border-border">
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider block">3. Embedded Compliance & Lineage Options:</span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {[
                    { label: 'Include AI Executive Summary', checked: includeAiSummary, set: setIncludeAiSummary, desc: 'Embed LLM narrative synthesis on cover page.' },
                    { label: 'Include Mathematical Formulas', checked: includeFormulas, set: setIncludeFormulas, desc: 'Embed KPI formula lineage & variable definitions.' },
                    { label: 'Include Data Quality Score Badge', checked: includeQualityBadge, set: setIncludeQualityBadge, desc: 'Embed 94/100 Enterprise PASS certification.' },
                    { label: 'Include SOC2 Audit Trail Stamp', checked: includeAuditStamp, set: setIncludeAuditStamp, desc: 'Embed timestamp and user ID watermark.' },
                  ].map((opt, idx) => (
                    <label
                      key={idx}
                      className={`flex items-start gap-3 p-3 rounded-xl border cursor-pointer transition-colors ${
                        opt.checked ? 'bg-muted/40 border-primary/40' : 'bg-card border-border'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={opt.checked}
                        onChange={(e) => opt.set(e.target.checked)}
                        className="w-4 h-4 mt-0.5 rounded text-primary focus:ring-primary border-input bg-background"
                      />
                      <div className="space-y-0.5">
                        <span className="text-xs font-bold text-foreground block">{opt.label}</span>
                        <span className="text-[10px] text-muted-foreground block leading-relaxed">{opt.desc}</span>
                      </div>
                    </label>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Scheduled Automated Delivery Setup */}
          <Card>
            <CardHeader className="pb-4 border-b border-border">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-base flex items-center gap-2">
                    <Calendar className="w-5 h-5 text-primary" />
                    <span>Scheduled Automated Email Delivery</span>
                  </CardTitle>
                  <CardDescription>Configure recurring report dispatch to executive stakeholders and Slack channels</CardDescription>
                </div>
                <Badge variant="purple">Automated Cron Engine</Badge>
              </div>
            </CardHeader>
            <CardContent className="p-6">
              <form onSubmit={handleSchedule} className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <Select label="Dispatch Frequency" value={scheduleFreq} onChange={(e) => setScheduleFreq(e.target.value)}>
                    <option value="DAILY">Daily at 08:00 AM UTC</option>
                    <option value="WEEKLY">Weekly on Monday at 08:00 AM UTC</option>
                    <option value="MONTHLY">Monthly on 1st at 08:00 AM UTC</option>
                    <option value="QUARTERLY">Quarterly Executive Review</option>
                  </Select>
                  <Select label="Target File Format" value={format} onChange={(e) => setFormat(e.target.value as any)}>
                    <option value="PDF">PDF Presentation Document</option>
                    <option value="EXCEL">Excel Data Workbook (.xlsx)</option>
                  </Select>
                </div>

                <div className="space-y-1">
                  <label className="text-xs font-bold text-foreground">Recipient Email List (Comma Separated)</label>
                  <input
                    type="text"
                    value={emailRecipients}
                    onChange={(e) => setEmailRecipients(e.target.value)}
                    className="w-full h-10 px-3 rounded-lg border border-input bg-background text-xs text-foreground focus:outline-none focus:ring-2 focus:ring-primary font-mono"
                    placeholder="executives@company.com, finance@company.com"
                    required
                  />
                </div>

                <div className="flex justify-end pt-2">
                  <Button type="submit" variant="primary" size="md" isLoading={isScheduling} leftIcon={<Mail className="w-4 h-4" />}>
                    Save Schedule & Activate Cron
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* Right 1 Col: Export History & Summary */}
        <div className="space-y-6">
          <Card className="border-primary/30 bg-gradient-to-br from-card to-primary/5">
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-purple-500" />
                <span>Export Summary & Verification</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-xs">
              <div className="p-3.5 rounded-xl bg-background border border-border space-y-2">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Selected Format:</span>
                  <span className="font-bold text-foreground">{format} Presentation</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Dashboard Scope:</span>
                  <span className="font-bold text-primary">{scope}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Compliance Lineage:</span>
                  <Badge variant="success" size="sm">100% Embedded</Badge>
                </div>
              </div>
              <p className="text-muted-foreground leading-relaxed">
                All generated documents are cryptographically signed with SOC2 Type II audit stamps to guarantee data provenance and prevent unauthorized modification.
              </p>
              <Button
                variant="primary"
                size="lg"
                onClick={handleExport}
                isLoading={isExporting}
                leftIcon={<Download className="w-4 h-4" />}
                className="w-full font-bold shadow-md"
              >
                Download Report Now
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3 border-b border-border">
              <CardTitle className="text-base flex items-center gap-2">
                <Clock className="w-4 h-4 text-muted-foreground" />
                <span>Recent Export History</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="p-4 space-y-3">
              {recentExports.map((ex, i) => (
                <div key={i} className="p-3 rounded-xl border border-border bg-card flex items-start justify-between gap-2">
                  <div className="space-y-1 truncate">
                    <span className="text-xs font-bold text-foreground block truncate" title={ex.name}>{ex.name}</span>
                    <span className="text-[10px] text-muted-foreground block">{ex.date} • by {ex.by}</span>
                  </div>
                  <Badge variant="outline" size="sm" className="shrink-0 font-mono">{ex.size}</Badge>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
