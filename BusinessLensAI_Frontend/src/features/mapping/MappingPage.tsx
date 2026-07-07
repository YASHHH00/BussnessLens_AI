import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { GitMerge, Sparkles, CheckCircle2, AlertTriangle, ArrowRight, Save, ShieldCheck, RefreshCw, Check, HelpCircle, Layers } from 'lucide-react';
import { Button, Select, Card, CardHeader, CardTitle, CardDescription, CardContent, Badge, toast, LoadingState, DomainSelector } from '../../shared/components';
import { mappingService } from '../../shared/lib/services/mappingService';
import { ColumnMapping, SchemaDriftAlert, AggregationType } from '../../shared/types';
import { useAppStore } from '../../shared/stores/useAppStore';

export const MappingPage: React.FC = () => {
  const navigate = useNavigate();
  const setWorkflowStep = useAppStore((s) => s.setWorkflowStep);

  const [mappings, setMappings] = useState<ColumnMapping[]>([]);
  const [driftAlert, setDriftAlert] = useState<SchemaDriftAlert | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSaving, setIsSaving] = useState<boolean>(false);

  // Available physical tables and columns in our mock PostgreSQL DB
  const availableColumns: { table: string; column: string; type: string }[] = [
    { table: 'orders', column: 'total_amount', type: 'DECIMAL' },
    { table: 'orders', column: 'net_profit', type: 'DECIMAL' },
    { table: 'orders', column: 'created_at', type: 'TIMESTAMP' },
    { table: 'orders', column: 'status', type: 'VARCHAR' },
    { table: 'customers', column: 'state_region', type: 'VARCHAR' },
    { table: 'customers', column: 'full_name', type: 'VARCHAR' },
    { table: 'marketing_spend', column: 'acquisition_cost', type: 'DECIMAL' },
    { table: 'products', column: 'category', type: 'VARCHAR' },
  ];

  useEffect(() => {
    setIsLoading(true);
    Promise.all([mappingService.getMappings('conn_pg_01'), mappingService.getSchemaDriftAlerts('conn_pg_01')])
      .then(([mapData, driftData]) => {
        setMappings(mapData);
        setDriftAlert(driftData);
        setIsLoading(false);
      })
      .catch(() => setIsLoading(false));
  }, []);

  const handleColumnChange = (mappingId: string, value: string) => {
    const [table, col] = value.split('.');
    setMappings((prev) =>
      prev.map((item) =>
        item.id === mappingId
          ? {
              ...item,
              mappedTableName: table || '',
              mappedColumnName: col || '',
              status: 'MODIFIED',
              isAiSuggested: false,
            }
          : item
      )
    );
    toast.info('Mapping Modified', `Mapped to physical column: ${value}`);
  };

  const handleAggChange = (mappingId: string, agg: AggregationType) => {
    setMappings((prev) =>
      prev.map((item) => (item.id === mappingId ? { ...item, aggregation: agg, status: 'MODIFIED' } : item))
    );
  };

  const confirmSingleMapping = (id: string) => {
    setMappings((prev) => prev.map((item) => (item.id === id ? { ...item, status: 'CONFIRMED' } : item)));
    toast.success('Mapping Confirmed', 'Business field locked to physical database schema.');
  };

  const confirmAllMappings = () => {
    setMappings((prev) => prev.map((item) => ({ ...item, status: 'CONFIRMED' })));
    toast.success('All Mappings Confirmed', 'All 5 business concepts are now locked and ready for Semantic Layer.');
  };

  const onSaveAndProceed = async () => {
    const unconfirmedCount = mappings.filter((m) => m.status === 'PENDING').length;
    if (unconfirmedCount > 0) {
      toast.warning('Mandatory Confirmation Required', `Please review and confirm the remaining ${unconfirmedCount} pending mappings before proceeding.`);
      return;
    }
    setIsSaving(true);
    try {
      await mappingService.saveAllMappings(mappings);
      toast.success('Smart Mapping Saved', 'Confirmed mappings saved to Smart Mapping Memory for future scans.');
      setWorkflowStep('SEMANTIC_LAYER');
      navigate('/semantic-explorer');
    } catch {
      toast.error('Save Failed', 'Could not save mapping configuration.');
    } finally {
      setIsSaving(false);
    }
  };

  const confirmedCount = mappings.filter((m) => m.status === 'CONFIRMED' || m.status === 'MODIFIED').length;
  const progressPercent = mappings.length > 0 ? Math.round((confirmedCount / mappings.length) * 100) : 0;

  return (
    <div className="space-y-8 max-w-7xl mx-auto animate-in fade-in-50 duration-300 pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Badge variant="purple">Step 3 & 4: AI Schema Mapping Review</Badge>
            <DomainSelector />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">AI Schema Mapping & Semantic Preview</h1>
          <p className="text-sm text-muted-foreground">
            Review and confirm AI-suggested mappings between physical PostgreSQL columns and standard Retail V1 business concepts.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button variant="outline" size="md" onClick={confirmAllMappings} leftIcon={<Check className="w-4 h-4 text-emerald-500" />}>
            Confirm All Suggested
          </Button>
          <Button
            variant="primary"
            size="md"
            onClick={onSaveAndProceed}
            isLoading={isSaving}
            rightIcon={<ArrowRight className="w-4 h-4" />}
          >
            Save & Open Semantic Layer
          </Button>
        </div>
      </div>

      {/* Smart Mapping Memory & Progress Banner */}
      <Card className="border-primary/30 bg-card">
        <CardContent className="p-6 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-purple-500/10 text-purple-500">
                <Sparkles className="w-6 h-6 animate-pulse" />
              </div>
              <div>
                <h3 className="text-base font-bold text-foreground">Smart Mapping Memory & AI Confidence</h3>
                <p className="text-xs text-muted-foreground">
                  Mandatory human-in-the-loop confirmation required. Confirmed mappings are cached for automatic future schema drift detection.
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Confirmation Status:</span>
              <Badge variant={progressPercent === 100 ? 'success' : 'warning'} size="md">
                {confirmedCount} / {mappings.length} Confirmed ({progressPercent}%)
              </Badge>
            </div>
          </div>

          <div className="h-2 w-full rounded-full bg-muted overflow-hidden">
            <div
              className={`h-full transition-all duration-300 ${progressPercent === 100 ? 'bg-emerald-500' : 'bg-primary'}`}
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </CardContent>
      </Card>

      {/* Schema Drift Alert Banner */}
      {driftAlert && (
        <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-start justify-between gap-4 text-xs text-amber-600 dark:text-amber-400 animate-in slide-in-from-top-2">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <span className="font-bold block text-sm">Schema Drift Alert Detected</span>
              <p className="text-muted-foreground leading-relaxed">
                Physical column changes detected on PostgreSQL connection <strong className="text-foreground">{driftAlert.connectionId}</strong>. 
                {driftAlert.changes.map((c, idx) => (
                  <span key={idx} className="block mt-0.5">
                    • In table <code className="font-mono bg-background/60 px-1 rounded">{c.tableName}</code>: column <code className="font-mono bg-background/60 px-1 rounded">{c.oldColumnName}</code> was {c.changeType.toLowerCase()} to <code className="font-mono bg-background/60 px-1 rounded">{c.newColumnName || 'deleted'}</code>.
                  </span>
                ))}
              </p>
            </div>
          </div>
          <Button variant="outline" size="sm" onClick={() => setDriftAlert(null)} className="shrink-0 text-xs">
            Dismiss Alert
          </Button>
        </div>
      )}

      {/* Virtualized Mapping Review Table */}
      <Card className="overflow-hidden border-border/80">
        <CardHeader className="p-6 pb-4 border-b border-border flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-base">Semantic Concept Mappings</CardTitle>
            <CardDescription>Match physical database fields to domain KPI requirements</CardDescription>
          </div>
          <Badge variant="info">5 Mandatory Fields</Badge>
        </CardHeader>
        <CardContent className="p-0 overflow-x-auto">
          {isLoading ? (
            <div className="p-6">
              <LoadingState type="table" count={5} />
            </div>
          ) : (
            <table className="w-full text-left text-xs border-collapse">
              <thead className="bg-muted/60 border-b border-border text-muted-foreground select-none">
                <tr>
                  <th className="p-4 font-semibold uppercase tracking-wider">Business Concept</th>
                  <th className="p-4 font-semibold uppercase tracking-wider">Physical DB Mapping</th>
                  <th className="p-4 font-semibold uppercase tracking-wider">Aggregation</th>
                  <th className="p-4 font-semibold uppercase tracking-wider">Sample Data Preview</th>
                  <th className="p-4 font-semibold uppercase tracking-wider">AI Confidence & Status</th>
                  <th className="p-4 font-semibold uppercase tracking-wider text-right">Human Review</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border bg-card">
                {mappings.map((m) => {
                  const currentMappedVal = `${m.mappedTableName}.${m.mappedColumnName}`;
                  const isConfirmed = m.status === 'CONFIRMED' || m.status === 'MODIFIED';

                  return (
                    <tr key={m.id} className={`hover:bg-muted/20 transition-colors ${isConfirmed ? 'bg-emerald-500/[0.02]' : ''}`}>
                      {/* 1. Business Concept */}
                      <td className="p-4 space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-sm text-foreground">{m.businessFieldName}</span>
                          {m.isForecastable && (
                            <Badge variant="purple" size="sm" title="Eligible for 90-Day AI Forecasting">
                              Forecastable
                            </Badge>
                          )}
                        </div>
                        <p className="text-[11px] text-muted-foreground max-w-xs leading-relaxed">{m.semanticDescription}</p>
                      </td>

                      {/* 2. Physical DB Mapping */}
                      <td className="p-4">
                        <Select
                          value={currentMappedVal}
                          onChange={(e) => handleColumnChange(m.id, e.target.value)}
                          className="w-56 text-xs font-mono font-semibold"
                        >
                          <option value="">-- Select Physical Column --</option>
                          {availableColumns.map((col, idx) => (
                            <option key={idx} value={`${col.table}.${col.column}`}>
                              {col.table}.{col.column} ({col.type})
                            </option>
                          ))}
                        </Select>
                      </td>

                      {/* 3. Aggregation */}
                      <td className="p-4">
                        <Select
                          value={m.aggregation}
                          onChange={(e) => handleAggChange(m.id, e.target.value as AggregationType)}
                          className="w-28 text-xs font-bold"
                        >
                          <option value="SUM">SUM</option>
                          <option value="AVG">AVG</option>
                          <option value="COUNT">COUNT</option>
                          <option value="MAX">MAX</option>
                          <option value="MIN">MIN</option>
                          <option value="NONE">NONE</option>
                        </Select>
                      </td>

                      {/* 4. Sample Data Preview */}
                      <td className="p-4 font-mono text-muted-foreground">
                        <div className="max-w-xs truncate bg-muted/50 p-1.5 rounded border border-border" title={m.sampleValues.join(', ')}>
                          {m.sampleValues.slice(0, 3).join(', ')}
                          {m.sampleValues.length > 3 && '...'}
                        </div>
                      </td>

                      {/* 5. AI Confidence & Status */}
                      <td className="p-4 space-y-1.5">
                        <div className="flex items-center gap-2">
                          <Badge variant={m.confidenceScore >= 90 ? 'success' : 'warning'} size="sm">
                            {m.confidenceScore}% Confident
                          </Badge>
                          {m.isAiSuggested && <span className="text-[10px] font-semibold text-purple-500">AI Suggested</span>}
                        </div>
                        <div>
                          {m.status === 'CONFIRMED' && <Badge variant="success">Confirmed</Badge>}
                          {m.status === 'MODIFIED' && <Badge variant="info">Modified</Badge>}
                          {m.status === 'PENDING' && <Badge variant="warning">Review Required</Badge>}
                        </div>
                      </td>

                      {/* 6. Human Review CTA */}
                      <td className="p-4 text-right">
                        {isConfirmed ? (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => confirmSingleMapping(m.id)}
                            className="h-8 text-xs text-emerald-600 dark:text-emerald-400 border-emerald-500/30 bg-emerald-500/5 gap-1"
                          >
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            Verified
                          </Button>
                        ) : (
                          <Button
                            variant="primary"
                            size="sm"
                            onClick={() => confirmSingleMapping(m.id)}
                            className="h-8 text-xs font-bold shadow-sm"
                          >
                            Confirm Mapping
                          </Button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </CardContent>
      </Card>

      {/* Footer Info */}
      <div className="p-4 rounded-xl bg-muted/30 border border-border flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-muted-foreground">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-500" />
          <span>Inline validation ensures all mandatory financial fields (Revenue, Margin) are correctly mapped before dashboard generation.</span>
        </div>
        <Button variant="outline" size="sm" onClick={() => navigate('/semantic-explorer')} leftIcon={<Layers className="w-4 h-4 text-blue-500" />}>
          Skip to Semantic Layer Explorer
        </Button>
      </div>
    </div>
  );
};
