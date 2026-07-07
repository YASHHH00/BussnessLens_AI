import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Database, Search, CheckCircle2, AlertTriangle, ArrowRight, Table as TableIcon, Key, ChevronDown, ChevronRight, Layers, ShieldCheck } from 'lucide-react';
import { Button, Card, CardHeader, CardTitle, CardDescription, CardContent, Badge, toast } from '../../shared/components';
import { useAppStore } from '../../shared/stores/useAppStore';

interface ColumnSchema {
  name: string;
  type: string;
  isPk?: boolean;
  isFk?: boolean;
  fkTarget?: string;
  nullPercentage: number;
}

interface TableSchema {
  name: string;
  rowCount: number;
  columns: ColumnSchema[];
  status: 'SCANNED' | 'WARNING' | 'SKIPPED';
  warningMsg?: string;
}

export const SchemaDetectionPage: React.FC = () => {
  const navigate = useNavigate();
  const setWorkflowStep = useAppStore((s) => s.setWorkflowStep);

  const [scanStep, setScanStep] = useState<number>(0);
  const [isScanning, setIsScanning] = useState<boolean>(true);
  const [expandedTables, setExpandedTables] = useState<Record<string, boolean>>({
    orders: true,
    customers: true,
  });

  const scanStepsList = [
    'Connecting to PostgreSQL database host (pg-prod.businesslens.ai:5432)...',
    'Scanning table 3 of 14: orders (15,420 rows)...',
    'Scanning table 8 of 14: customers (4,200 rows)...',
    'Extracting primary & foreign key relationships across 14 tables...',
    'Analyzing column nullability & statistical data distributions...',
    'Schema scan & metadata extraction completed successfully!',
  ];

  const mockDetectedTables: TableSchema[] = [
    {
      name: 'orders',
      rowCount: 15420,
      status: 'SCANNED',
      columns: [
        { name: 'id', type: 'UUID', isPk: true, nullPercentage: 0 },
        { name: 'customer_id', type: 'UUID', isFk: true, fkTarget: 'customers.id', nullPercentage: 0 },
        { name: 'total_amount', type: 'DECIMAL(10,2)', nullPercentage: 0 },
        { name: 'net_profit', type: 'DECIMAL(10,2)', nullPercentage: 0 },
        { name: 'status', type: 'VARCHAR(50)', nullPercentage: 0 },
        { name: 'created_at', type: 'TIMESTAMP WITH TIME ZONE', nullPercentage: 0 },
        { name: 'discount_code', type: 'VARCHAR(20)', nullPercentage: 57.7 },
      ],
    },
    {
      name: 'customers',
      rowCount: 4200,
      status: 'SCANNED',
      columns: [
        { name: 'id', type: 'UUID', isPk: true, nullPercentage: 0 },
        { name: 'email', type: 'VARCHAR(255)', nullPercentage: 0 },
        { name: 'full_name', type: 'VARCHAR(150)', nullPercentage: 0 },
        { name: 'state_region', type: 'VARCHAR(50)', nullPercentage: 0 },
        { name: 'customer_phone', type: 'VARCHAR(20)', nullPercentage: 3.1 },
        { name: 'created_at', type: 'TIMESTAMP WITH TIME ZONE', nullPercentage: 0 },
      ],
    },
    {
      name: 'products',
      rowCount: 350,
      status: 'SCANNED',
      columns: [
        { name: 'id', type: 'UUID', isPk: true, nullPercentage: 0 },
        { name: 'sku', type: 'VARCHAR(50)', nullPercentage: 0 },
        { name: 'product_name', type: 'VARCHAR(200)', nullPercentage: 0 },
        { name: 'category', type: 'VARCHAR(100)', nullPercentage: 0 },
        { name: 'unit_price', type: 'DECIMAL(10,2)', nullPercentage: 0 },
        { name: 'inventory_count', type: 'INTEGER', nullPercentage: 0 },
      ],
    },
    {
      name: 'marketing_spend',
      rowCount: 120,
      status: 'SCANNED',
      columns: [
        { name: 'campaign_id', type: 'VARCHAR(50)', isPk: true, nullPercentage: 0 },
        { name: 'channel', type: 'VARCHAR(50)', nullPercentage: 0 },
        { name: 'cost', type: 'DECIMAL(10,2)', nullPercentage: 0 },
        { name: 'acquisition_cost', type: 'DECIMAL(10,2)', nullPercentage: 0 },
        { name: 'date_period', type: 'DATE', nullPercentage: 0 },
      ],
    },
    {
      name: 'legacy_audit_logs',
      rowCount: 0,
      status: 'SKIPPED',
      warningMsg: 'Table skipped due to missing read permissions on legacy schema.',
      columns: [],
    },
    {
      name: 'user_sessions_tmp',
      rowCount: 89000,
      status: 'WARNING',
      warningMsg: 'High null percentage (84.2%) detected across session telemetry columns.',
      columns: [
        { name: 'session_id', type: 'VARCHAR(100)', isPk: true, nullPercentage: 0 },
        { name: 'user_id', type: 'UUID', nullPercentage: 84.2 },
        { name: 'ip_address', type: 'VARCHAR(45)', nullPercentage: 12.0 },
      ],
    },
  ];

  useEffect(() => {
    let current = 0;
    const interval = setInterval(() => {
      current += 1;
      if (current < scanStepsList.length) {
        setScanStep(current);
      } else {
        setIsScanning(false);
        clearInterval(interval);
        toast.success('Schema Detection Ready', 'Metadata extracted for 14 tables and 82 columns.');
      }
    }, 600);

    return () => clearInterval(interval);
  }, []);

  const toggleTable = (tableName: string) => {
    setExpandedTables((prev) => ({ ...prev, [tableName]: !prev[tableName] }));
  };

  const onProceedToMapping = () => {
    setWorkflowStep('MAPPING_REVIEW');
    navigate('/mapping');
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto animate-in fade-in-50 duration-300 pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <Badge variant="purple">Step 2: Schema Detection</Badge>
          <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">Real-Time Schema & Metadata Scan</h1>
          <p className="text-sm text-muted-foreground">
            Automatic extraction of tables, primary/foreign key relationships, and data quality distributions.
          </p>
        </div>
        <Button
          variant="primary"
          size="md"
          onClick={onProceedToMapping}
          disabled={isScanning}
          rightIcon={<ArrowRight className="w-4 h-4" />}
        >
          Proceed to AI Schema Mapping
        </Button>
      </div>

      {/* Real-time Scanning Progress Box */}
      <Card className="border-primary/30 bg-card">
        <CardContent className="p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`p-2.5 rounded-xl ${isScanning ? 'bg-primary/10 text-primary animate-spin' : 'bg-emerald-500/10 text-emerald-500'}`}>
                {isScanning ? <Search className="w-6 h-6" /> : <CheckCircle2 className="w-6 h-6" />}
              </div>
              <div>
                <h3 className="text-base font-bold text-foreground">
                  {isScanning ? 'Scanning Database Engine...' : 'Metadata Extraction Complete'}
                </h3>
                <p className="text-xs font-mono text-primary mt-0.5">{scanStepsList[scanStep]}</p>
              </div>
            </div>
            <Badge variant={isScanning ? 'info' : 'success'} size="md">
              {isScanning ? `Step ${scanStep + 1} of ${scanStepsList.length}` : '100% Scanned'}
            </Badge>
          </div>

          <div className="h-2.5 w-full rounded-full bg-muted overflow-hidden">
            <div
              className={`h-full transition-all duration-300 ${isScanning ? 'bg-primary' : 'bg-emerald-500'}`}
              style={{ width: `${Math.min(100, ((scanStep + 1) / scanStepsList.length) * 100)}%` }}
            />
          </div>

          {/* Quick stats summary */}
          {!isScanning && (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2 border-t border-border text-center">
              <div className="p-3 rounded-lg bg-muted/40">
                <span className="text-xs text-muted-foreground block">Tables Scanned</span>
                <strong className="text-base text-foreground font-extrabold">14 Tables</strong>
              </div>
              <div className="p-3 rounded-lg bg-muted/40">
                <span className="text-xs text-muted-foreground block">Columns Extracted</span>
                <strong className="text-base text-foreground font-extrabold">82 Columns</strong>
              </div>
              <div className="p-3 rounded-lg bg-muted/40">
                <span className="text-xs text-muted-foreground block">Relationships Found</span>
                <strong className="text-base text-primary font-extrabold">12 FK Pairs</strong>
              </div>
              <div className="p-3 rounded-lg bg-muted/40">
                <span className="text-xs text-muted-foreground block">Partial Warnings</span>
                <strong className="text-base text-amber-500 font-extrabold">2 Tables Skipped</strong>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Partial failure warning banner */}
      <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-start gap-3 text-xs text-amber-600 dark:text-amber-400">
        <AlertTriangle className="w-5 h-5 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <span className="font-bold block">Partial Scan Warnings Detected</span>
          <p className="text-muted-foreground leading-relaxed">
            Table <code className="font-mono bg-background/60 px-1 rounded">legacy_audit_logs</code> was skipped due to restricted read permissions. Table <code className="font-mono bg-background/60 px-1 rounded">user_sessions_tmp</code> contains null percentages exceeding 80%. These will not affect core KPI calculations.
          </p>
        </div>
      </div>

      {/* Collapsible Schema Tree Explorer */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold tracking-tight text-foreground flex items-center gap-2">
            <Layers className="w-5 h-5 text-primary" />
            <span>Extracted Schema Tree & Relationships</span>
          </h2>
          <span className="text-xs text-muted-foreground">Click any table to inspect physical column data types and keys</span>
        </div>

        <div className="space-y-3">
          {mockDetectedTables.map((tbl) => {
            const isExpanded = !!expandedTables[tbl.name];
            return (
              <Card key={tbl.name} className="overflow-hidden border-border/80">
                {/* Table Header Row */}
                <div
                  onClick={() => toggleTable(tbl.name)}
                  className="p-4 bg-card hover:bg-muted/40 cursor-pointer transition-colors flex items-center justify-between select-none"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-muted-foreground">
                      {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                    </span>
                    <div className="p-2 rounded-lg bg-primary/10 text-primary">
                      <TableIcon className="w-4 h-4" />
                    </div>
                    <div>
                      <h3 className="text-sm font-bold font-mono text-foreground">{tbl.name}</h3>
                      <span className="text-xs text-muted-foreground">
                        {tbl.rowCount.toLocaleString()} rows • {tbl.columns.length} columns
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    {tbl.status === 'SCANNED' && <Badge variant="success">Scanned OK</Badge>}
                    {tbl.status === 'WARNING' && <Badge variant="warning">Null Warning</Badge>}
                    {tbl.status === 'SKIPPED' && <Badge variant="danger">Skipped</Badge>}
                  </div>
                </div>

                {/* Warning message if any */}
                {tbl.warningMsg && isExpanded && (
                  <div className="px-4 py-2 bg-amber-500/5 border-t border-amber-500/10 text-xs text-amber-600 dark:text-amber-400 flex items-center gap-2 font-medium">
                    <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                    <span>{tbl.warningMsg}</span>
                  </div>
                )}

                {/* Expanded Column List */}
                {isExpanded && tbl.columns.length > 0 && (
                  <div className="border-t border-border bg-muted/10 overflow-x-auto">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-muted/50 border-b border-border text-muted-foreground">
                        <tr>
                          <th className="p-3 font-semibold">Column Name</th>
                          <th className="p-3 font-semibold">Physical Data Type</th>
                          <th className="p-3 font-semibold">Key Relationship</th>
                          <th className="p-3 font-semibold">Null Consistency</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-border bg-card">
                        {tbl.columns.map((col) => (
                          <tr key={col.name} className="hover:bg-muted/20 font-mono">
                            <td className="p-3 font-bold text-foreground flex items-center gap-2">
                              {col.isPk && <span title="Primary Key"><Key className="w-3.5 h-3.5 text-amber-500 shrink-0" /></span>}
                              {col.isFk && <span title={`Foreign Key -> ${col.fkTarget}`}><Key className="w-3.5 h-3.5 text-blue-500 shrink-0" /></span>}
                              <span>{col.name}</span>
                            </td>
                            <td className="p-3 text-muted-foreground">{col.type}</td>
                            <td className="p-3 font-sans">
                              {col.isPk && <Badge variant="warning" size="sm">Primary Key</Badge>}
                              {col.isFk && (
                                <Badge variant="info" size="sm">
                                  FK → {col.fkTarget}
                                </Badge>
                              )}
                              {!col.isPk && !col.isFk && <span className="text-muted-foreground/60">—</span>}
                            </td>
                            <td className="p-3 font-sans">
                              {col.nullPercentage === 0 ? (
                                <span className="text-emerald-500 font-semibold flex items-center gap-1">
                                  <CheckCircle2 className="w-3.5 h-3.5" /> 0% Null (100% Valid)
                                </span>
                              ) : col.nullPercentage < 10 ? (
                                <span className="text-amber-500 font-medium">{col.nullPercentage}% Null</span>
                              ) : (
                                <span className="text-destructive font-bold">{col.nullPercentage}% Null (High)</span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </Card>
            );
          })}
        </div>
      </div>

      {/* Bottom CTA */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-card to-primary/10 border border-border flex flex-col sm:flex-row items-center justify-between gap-4 shadow-sm">
        <div className="space-y-1">
          <h3 className="text-base font-bold text-foreground flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-500" />
            <span>Schema Scan Verified</span>
          </h3>
          <p className="text-xs text-muted-foreground">
            Ready to let the AI engine suggest column mappings and KPI definitions for the Retail V1 Domain?
          </p>
        </div>
        <Button
          variant="primary"
          size="lg"
          onClick={onProceedToMapping}
          disabled={isScanning}
          rightIcon={<ArrowRight className="w-4 h-4" />}
          className="w-full sm:w-auto font-bold"
        >
          Continue to Step 3: AI Schema Mapping
        </Button>
      </div>
    </div>
  );
};
