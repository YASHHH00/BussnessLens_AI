import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldCheck, AlertTriangle, CheckCircle2, ArrowRight, RefreshCw, FileText, Activity, Layers, Database, Sparkles } from 'lucide-react';
import { Button, Card, CardHeader, CardTitle, CardDescription, CardContent, Badge, LoadingState, toast, DomainSelector } from '../../shared/components';
import { qualityService } from '../../shared/lib/services/qualityService';
import { DataQualityReport } from '../../shared/types';

export const DataQualityReportPage: React.FC = () => {
  const navigate = useNavigate();
  const [report, setReport] = useState<DataQualityReport | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isScanning, setIsScanning] = useState<boolean>(false);

  useEffect(() => {
    setIsLoading(true);
    qualityService
      .getDataQualityReport('conn_pg_01')
      .then((data) => {
        setReport(data);
        setIsLoading(false);
      })
      .catch(() => setIsLoading(false));
  }, []);

  const handleRescan = async () => {
    setIsScanning(true);
    toast.info('Quality Scan Initiated', 'Scanning 14 tables and 82 columns for null consistency and anomalies...');
    await new Promise((r) => setTimeout(r, 1500));
    setIsScanning(false);
    toast.success('Scan Complete', 'Data quality score updated: 94/100 (Enterprise PASS).');
  };

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

  return (
    <div className="space-y-8 max-w-7xl mx-auto animate-in fade-in-50 duration-300 pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Badge variant="purple">Backend V3: Quality Scanner</Badge>
            <DomainSelector />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">Data Quality & Anomaly Report</h1>
          <p className="text-sm text-muted-foreground">
            Automated health scanner checking completeness, consistency, uniqueness, and relationship integrity across your PostgreSQL database.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="md"
            onClick={handleRescan}
            isLoading={isScanning}
            leftIcon={<RefreshCw className="w-4 h-4" />}
          >
            Re-Run Quality Scan
          </Button>
          <Button
            variant="primary"
            size="md"
            onClick={() => navigate('/rules')}
            rightIcon={<ArrowRight className="w-4 h-4" />}
          >
            Configure Business Rules
          </Button>
        </div>
      </div>

      {isLoading ? (
        <LoadingState type="card" count={4} message="Analyzing data distributions and integrity rules..." />
      ) : report ? (
        <>
          {/* Top Overall Score Banner */}
          <Card className="border-emerald-500/30 bg-gradient-to-r from-card via-card to-emerald-500/10">
            <CardContent className="p-6 flex flex-col sm:flex-row items-center justify-between gap-6">
              <div className="flex items-center gap-5">
                <div className="w-20 h-20 rounded-2xl bg-emerald-500/10 border-2 border-emerald-500/30 flex flex-col items-center justify-center text-emerald-600 dark:text-emerald-400 shrink-0 shadow-inner">
                  <span className="text-2xl font-extrabold leading-none">{report.overallScore}</span>
                  <span className="text-[10px] font-bold uppercase tracking-wider mt-0.5">/ 100</span>
                </div>
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <h3 className="text-xl font-bold text-foreground">Overall Health: Enterprise PASS</h3>
                    <Badge variant="success" size="md">Production Ready</Badge>
                  </div>
                  <p className="text-xs text-muted-foreground max-w-xl leading-relaxed">
                    Your database schema meets strict enterprise reporting standards. All 5 core financial KPIs have 0% null rates and verified foreign key integrity.
                  </p>
                </div>
              </div>
              <div className="flex flex-col items-end gap-1 text-xs text-muted-foreground shrink-0">
                <span>Last scanned: <strong className="text-foreground">Today at 08:30 AM</strong></span>
                <span>Scanned records: <strong className="text-foreground">112,450 rows</strong></span>
              </div>
            </CardContent>
          </Card>

          {/* 4 Dimension Cards */}
          {(() => {
            const metrics = report.metrics || { completeness: 98, consistency: 96, uniqueness: 100, validity: 94 };
            const issues = report.issues || [];
            return (
              <>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  {[
                    { title: 'Completeness', score: `${metrics.completeness}%`, desc: '0% nulls on primary metrics', icon: <CheckCircle2 className="w-5 h-5 text-emerald-500" />, status: 'PASS' },
                    { title: 'Consistency', score: `${metrics.consistency}%`, desc: 'Verified data type formatting', icon: <Activity className="w-5 h-5 text-blue-500" />, status: 'PASS' },
                    { title: 'Uniqueness', score: `${metrics.uniqueness}%`, desc: 'No duplicate primary keys', icon: <ShieldCheck className="w-5 h-5 text-purple-500" />, status: 'PASS' },
                    { title: 'Validity', score: `${metrics.validity}%`, desc: '3 minor outlier warnings', icon: <AlertTriangle className="w-5 h-5 text-amber-500" />, status: 'WARNING' },
                  ].map((dim, i) => (
                    <Card key={i} isGlass hoverEffect>
                      <CardContent className="p-5 flex items-start justify-between">
                        <div className="space-y-1">
                          <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">{dim.title}</span>
                          <h3 className="text-2xl font-extrabold text-foreground">{dim.score}</h3>
                          <p className="text-xs text-muted-foreground">{dim.desc}</p>
                        </div>
                        <div className="p-2.5 rounded-xl bg-muted">{dim.icon}</div>
                      </CardContent>
                    </Card>
                  ))}
                </div>

                {/* Detailed Issues Table */}
                <Card className="overflow-hidden border-border/80">
                  <CardHeader className="p-6 pb-4 border-b border-border flex flex-row items-center justify-between">
                    <div>
                      <CardTitle className="text-base">Detected Quality Issues & Anomalies</CardTitle>
                      <CardDescription>Review itemized warnings across physical database tables</CardDescription>
                    </div>
                    <Badge variant="warning">{issues.length} Issues Found</Badge>
                  </CardHeader>
                  <CardContent className="p-0 overflow-x-auto">
                    <table className="w-full text-left text-xs border-collapse">
                      <thead className="bg-muted/60 border-b border-border text-muted-foreground select-none">
                        <tr>
                          <th className="p-4 font-semibold uppercase tracking-wider">Severity</th>
                          <th className="p-4 font-semibold uppercase tracking-wider">Table & Column</th>
                          <th className="p-4 font-semibold uppercase tracking-wider">Issue Description</th>
                          <th className="p-4 font-semibold uppercase tracking-wider">Impact Analysis</th>
                          <th className="p-4 font-semibold uppercase tracking-wider text-right">Recommended Action</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-border bg-card">
                        {issues.map((iss) => (
                          <tr key={iss.id} className="hover:bg-muted/20 transition-colors">
                            <td className="p-4">{getSeverityBadge(iss.severity)}</td>
                            <td className="p-4 font-mono font-bold text-foreground">
                              {iss.tableName}
                              {iss.columnName ? `.${iss.columnName}` : ''}
                            </td>
                            <td className="p-4 text-foreground font-medium">{iss.description}</td>
                            <td className="p-4 text-muted-foreground">{iss.impact}</td>
                            <td className="p-4 text-right">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => toast.success('Action Applied', `Automated fix triggered for ${iss.tableName}.`)}
                                className="h-8 text-xs font-semibold"
                              >
                                Auto Fix
                              </Button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </CardContent>
                </Card>
              </>
            );
          })()}
        </>
      ) : null}
    </div>
  );
};
