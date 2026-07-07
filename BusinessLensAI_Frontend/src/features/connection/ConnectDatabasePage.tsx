import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Database, Upload, CheckCircle2, AlertCircle, RefreshCw, ShieldCheck, FileSpreadsheet, ArrowRight, Trash2, HardDrive, HelpCircle, Server } from 'lucide-react';
import Papa from 'papaparse';
import * as XLSX from 'xlsx';
import { Button, Input, Select, Card, CardHeader, CardTitle, CardDescription, CardContent, Badge, toast, LoadingState, DomainSelector } from '../../shared/components';
import { connectionService } from '../../shared/lib/services/connectionService';
import { DatabaseConnection, DBType } from '../../shared/types';
import { useAppStore } from '../../shared/stores/useAppStore';

const dbSchema = z.object({
  name: z.string().min(3, { message: 'Connection display name is required.' }),
  type: z.enum(['POSTGRESQL', 'MYSQL', 'SQLSERVER', 'ORACLE', 'SQLITE'] as const),
  host: z.string().min(1, { message: 'Database host / IP is required.' }),
  port: z.number().int().min(1, { message: 'Port must be between 1 and 65535.' }).max(65535, { message: 'Port must be <= 65535.' }),
  databaseName: z.string().min(1, { message: 'Database name is required.' }),
  username: z.string().min(1, { message: 'Username is required.' }),
  password: z.string().optional(),
  sslMode: z.enum(['disable', 'require', 'verify-full'] as const).default('require'),
  isReadOnly: z.boolean().default(true),
});

type DBFormValues = z.infer<typeof dbSchema>;

export const ConnectDatabasePage: React.FC = () => {
  const navigate = useNavigate();
  const setWorkflowStep = useAppStore((s) => s.setWorkflowStep);
  const setActiveConnectionId = useAppStore((s) => s.setActiveConnectionId);

  const [activeTab, setActiveTab] = useState<'database' | 'file'>('database');
  const [connections, setConnections] = useState<DatabaseConnection[]>([]);
  const [isLoadingList, setIsLoadingList] = useState(true);

  const [testStatus, setTestStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle');
  const [testMessage, setTestMessage] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  // File upload state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [filePreview, setFilePreview] = useState<{ columns: string[]; rows: Record<string, unknown>[] } | null>(null);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<any>({
    resolver: zodResolver(dbSchema),
    defaultValues: {
      name: 'Production E-Commerce Analytics (PostgreSQL)',
      type: 'POSTGRESQL',
      host: 'pg-prod.businesslens.ai',
      port: 5432,
      databaseName: 'retail_analytics_db',
      username: 'bl_analytics_read',
      password: 'demo_password_123',
      sslMode: 'require',
      isReadOnly: true,
    },
  });

  const selectedType = watch('type');

  useEffect(() => {
    setIsLoadingList(true);
    connectionService
      .getConnections()
      .then((data) => {
        setConnections(data);
        setIsLoadingList(false);
      })
      .catch(() => setIsLoadingList(false));
  }, []);

  const onTestConnection = async () => {
    setTestStatus('testing');
    setTestMessage(null);
    try {
      const values = watch();
      const res = await connectionService.testConnection(values as unknown as Parameters<typeof connectionService.testConnection>[0]);
      if (res.success) {
        setTestStatus('success');
        setTestMessage(res.message);
        toast.success('Connection Successful', res.message);
      } else {
        setTestStatus('error');
        setTestMessage(res.message);
        toast.error('Connection Failed', res.message);
      }
    } catch (err: unknown) {
      setTestStatus('error');
      const msg = err && typeof err === 'object' && 'message' in err ? String(err.message) : 'Connection timed out or host unreachable.';
      setTestMessage(msg);
      toast.error('Connection Error', msg);
    }
  };

  const onSaveConnection = async (data: DBFormValues) => {
    if (testStatus !== 'success') {
      toast.warning('Test Required', 'Please successfully test the database connection before saving.');
      return;
    }
    setIsSaving(true);
    try {
      const newConn = await connectionService.saveConnection(data as unknown as Parameters<typeof connectionService.saveConnection>[0]);
      setConnections((prev) => [newConn, ...prev]);
      setActiveConnectionId(newConn.id || 'conn_pg_01');
      toast.success('Connection Saved', `${data.name} is now active.`);
      setWorkflowStep('SCHEMA_DETECT');
      navigate('/schema-detection');
    } catch {
      toast.error('Save Failed', 'Unable to save connection parameters.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleFileDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const processFile = (file: File) => {
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (!['csv', 'xlsx', 'xls'].includes(ext || '')) {
      toast.error('Invalid Format', 'Please upload a valid CSV or Excel spreadsheet file.');
      return;
    }
    setSelectedFile(file);
    toast.info('File Selected', `Parsing sample rows from ${file.name}...`);

    if (ext === 'csv') {
      Papa.parse(file, {
        header: true,
        preview: 10,
        complete: (results) => {
          const rows = results.data as Record<string, unknown>[];
          const columns = results.meta.fields || Object.keys(rows[0] || {});
          setFilePreview({ columns, rows });
        },
        error: () => toast.error('Parse Error', 'Could not parse CSV file.'),
      });
    } else {
      const reader = new FileReader();
      reader.onload = (e) => {
        const data = new Uint8Array(e.target?.result as ArrayBuffer);
        const workbook = XLSX.read(data, { type: 'array' });
        const firstSheetName = workbook.SheetNames[0] || 'Sheet1';
        const worksheet = workbook.Sheets[firstSheetName];
        if (!worksheet) return;
        const json = XLSX.utils.sheet_to_json<any[]>(worksheet, { header: 1 });
        const headers = (json[0] as string[]) || [];
        const sampleRows = json.slice(1, 11).map((rowArr) => {
          const obj: Record<string, unknown> = {};
          headers.forEach((h, idx) => {
            obj[h] = (rowArr as any[])[idx];
          });
          return obj;
        });
        setFilePreview({ columns: headers, rows: sampleRows });
      };
      reader.readAsArrayBuffer(file);
    }
  };

  const onConfirmFileUpload = async () => {
    if (!selectedFile) return;
    setIsUploading(true);
    try {
      const conn = (await connectionService.uploadFile(selectedFile)) as unknown as DatabaseConnection;
      setConnections((prev) => [conn, ...prev]);
      setActiveConnectionId((conn as any).id || (conn as any).fileId || 'conn_file_01');
      toast.success('File Imported', `${selectedFile.name} schema analyzed and registered.`);
      setWorkflowStep('SCHEMA_DETECT');
      navigate('/schema-detection');
    } catch {
      toast.error('Import Failed', 'Could not upload data file.');
    } finally {
      setIsUploading(false);
    }
  };

  const dbTypes = [
    { value: 'POSTGRESQL', label: 'PostgreSQL (Enterprise v15+)', icon: '🐘', port: 5432, desc: 'Primary transactional analytics engine' },
    { value: 'MYSQL', label: 'MySQL / MariaDB (v8.0+)', icon: '🐬', port: 3306, desc: 'Web commerce database replicas' },
    { value: 'ORACLE', label: 'Oracle Database (19c / 23c)', icon: '🔴', port: 1521, desc: 'Enterprise ERP & Financial ledger systems' },
    { value: 'SQLSERVER', label: 'Microsoft SQL Server (2022)', icon: '🪟', port: 1433, desc: 'Corporate data warehouse & OLAP cubes' },
    { value: 'SQLITE', label: 'SQLite / DuckDB (Local File)', icon: '🪶', port: 0, desc: 'Embedded analytical dataset storage' },
  ];

  return (
    <div className="space-y-8 animate-in fade-in-50 duration-300 pb-12">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 border border-indigo-500/20 shadow-xl relative overflow-hidden">
        <div className="absolute -right-10 -bottom-10 w-60 h-60 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="space-y-1 z-10">
          <div className="flex items-center gap-2">
            <Badge variant="info" size="sm" className="bg-indigo-500/20 text-indigo-300 border-indigo-500/30">
              Step 1 of 10 • Workflow Gate
            </Badge>
            <span className="text-xs text-slate-400 font-mono">Backend V3 Aligned</span>
          </div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight flex items-center gap-2.5">
            <Database className="w-7 h-7 text-indigo-400" />
            <span>Connect Data Source</span>
          </h1>
          <p className="text-sm text-slate-300 max-w-2xl leading-relaxed">
            Establish secure, read-only connections to enterprise database engines or ingest local flat spreadsheets. All queries are strictly audited and isolated.
          </p>
        </div>

        <div className="flex items-center gap-3 z-10">
          <Button variant="outline" size="sm" onClick={() => toast.info('Documentation', 'Opening enterprise connection firewall guide.')}>
            <HelpCircle className="w-4 h-4 mr-1.5" />
            Firewall & IP Whitelist
          </Button>
        </div>
      </div>

      {/* Connection Type Tabs */}
      <div className="flex items-center gap-2 border-b border-border pb-px">
        <button
          onClick={() => setActiveTab('database')}
          className={`flex items-center gap-2 px-5 py-3 text-sm font-semibold border-b-2 transition-all ${
            activeTab === 'database'
              ? 'border-primary text-primary bg-primary/5 rounded-t-lg'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <Server className="w-4 h-4" />
          <span>Database Servers ({connections.length})</span>
        </button>
        <button
          onClick={() => setActiveTab('file')}
          className={`flex items-center gap-2 px-5 py-3 text-sm font-semibold border-b-2 transition-all ${
            activeTab === 'file'
              ? 'border-primary text-primary bg-primary/5 rounded-t-lg'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <FileSpreadsheet className="w-4 h-4" />
          <span>Upload Excel / CSV</span>
          <Badge variant="success" size="sm">Instant Ingest</Badge>
        </button>
      </div>

      {activeTab === 'database' ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Form Area */}
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader className="pb-4 border-b border-border">
                <CardTitle className="text-base">Database Engine Parameters</CardTitle>
                <CardDescription>Enter credentials for your read-only analytics database user.</CardDescription>
              </CardHeader>
              <CardContent className="pt-6">
                <form onSubmit={handleSubmit((data) => onSaveConnection(data as any))} className="space-y-4">
                  <Input
                    label="Connection Display Name"
                    placeholder="e.g. Production Retail DB"
                    error={errors.name?.message ? String(errors.name?.message) : undefined}
                    {...register('name')}
                  />

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div className="sm:col-span-1">
                      <Select label="Database Engine" {...register('type')}>
                        <option value="POSTGRESQL">PostgreSQL (V1 Supported)</option>
                        <option value="MYSQL">MySQL (Future Ready)</option>
                        <option value="SQLSERVER">SQL Server (Future Ready)</option>
                        <option value="ORACLE">Oracle DB (Future Ready)</option>
                        <option value="SQLITE">SQLite (Future Ready)</option>
                      </Select>
                    </div>
                    <div className="sm:col-span-2">
                      <Input
                        label="Host / Server Address"
                        placeholder="pg-prod.businesslens.ai"
                        error={errors.host?.message ? String(errors.host?.message) : undefined}
                        {...register('host')}
                      />
                    </div>
                  </div>

                  {selectedType !== 'POSTGRESQL' && (
                    <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center gap-2 text-xs text-amber-600 dark:text-amber-400">
                      <AlertCircle className="w-4 h-4 shrink-0" />
                      <span>Note: Version 1 officially supports PostgreSQL. Selecting {selectedType} will use simulated future compatibility.</span>
                    </div>
                  )}

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <Input
                      label="Port Number"
                      type="number"
                      placeholder="5432"
                      error={errors.port?.message ? String(errors.port?.message) : undefined}
                      {...register('port', { valueAsNumber: true })}
                    />
                    <div className="sm:col-span-2">
                      <Input
                        label="Database Name"
                        placeholder="retail_analytics_db"
                        error={errors.databaseName?.message ? String(errors.databaseName?.message) : undefined}
                        {...register('databaseName')}
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <Input
                      label="Username"
                      placeholder="bl_analytics_read"
                      error={errors.username?.message ? String(errors.username?.message) : undefined}
                      {...register('username')}
                    />
                    <Input
                      label="Password"
                      type="password"
                      placeholder="••••••••"
                      error={errors.password?.message ? String(errors.password?.message) : undefined}
                      {...register('password')}
                    />
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 border-t border-border">
                    <Select label="SSL Encryption Mode" {...register('sslMode')}>
                      <option value="require">Require SSL (Recommended)</option>
                      <option value="verify-full">Verify Full Certificate</option>
                      <option value="disable">Disable SSL (Insecure)</option>
                    </Select>
                    <div className="flex items-center gap-2 pt-6">
                      <input
                        type="checkbox"
                        id="isReadOnly"
                        {...register('isReadOnly')}
                        className="w-4 h-4 text-primary focus:ring-primary rounded border-input bg-background"
                      />
                      <label htmlFor="isReadOnly" className="text-xs font-semibold text-foreground cursor-pointer">
                        Enforce Read-Only Access Gate
                      </label>
                    </div>
                  </div>

                  {/* Test status banner */}
                  {testStatus !== 'idle' && (
                    <div
                      className={`p-4 rounded-xl border text-xs flex items-start gap-3 ${
                        testStatus === 'testing'
                          ? 'bg-blue-500/10 border-blue-500/20 text-blue-600 dark:text-blue-400'
                          : testStatus === 'success'
                          ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-600 dark:text-emerald-400'
                          : 'bg-destructive/10 border-destructive/20 text-destructive'
                      }`}
                    >
                      {testStatus === 'testing' && <RefreshCw className="w-4 h-4 animate-spin shrink-0 mt-0.5" />}
                      {testStatus === 'success' && <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" />}
                      {testStatus === 'error' && <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />}
                      <div className="space-y-0.5">
                        <span className="font-bold">
                          {testStatus === 'testing'
                            ? 'Testing Database Connection...'
                            : testStatus === 'success'
                            ? 'Connection Verified'
                            : 'Connection Test Failed'}
                        </span>
                        {testMessage && <p className="text-muted-foreground">{testMessage}</p>}
                      </div>
                    </div>
                  )}

                  <div className="flex flex-wrap items-center justify-end gap-3 pt-4 border-t border-border">
                    <Button
                      type="button"
                      variant="outline"
                      size="md"
                      onClick={onTestConnection}
                      isLoading={testStatus === 'testing'}
                      leftIcon={<RefreshCw className="w-4 h-4" />}
                    >
                      Test Connection
                    </Button>
                    <Button
                      type="submit"
                      variant="primary"
                      size="md"
                      disabled={testStatus !== 'success'}
                      isLoading={isSaving}
                      rightIcon={<ArrowRight className="w-4 h-4" />}
                    >
                      Save & Proceed to Schema Scan
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </div>

          {/* Saved Connections Sidebar */}
          <div className="space-y-6">
            <Card>
              <CardHeader className="pb-3 border-b border-border">
                <CardTitle className="text-base">Saved Connections</CardTitle>
                <CardDescription>Select an active database to scan.</CardDescription>
              </CardHeader>
              <CardContent className="pt-4 space-y-3">
                {isLoadingList ? (
                  <LoadingState type="list" count={2} />
                ) : (
                  connections.map((conn) => (
                    <div
                      key={conn.id}
                      onClick={() => {
                        setActiveConnectionId(conn.id || 'conn_pg_01');
                        toast.info('Connection Selected', `${conn.name} is now active.`);
                        setWorkflowStep('SCHEMA_DETECT');
                        navigate('/schema-detection');
                      }}
                      className="p-3.5 rounded-xl border border-border bg-card hover:border-primary/50 cursor-pointer transition-all space-y-2 group"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-2">
                          <HardDrive className="w-4 h-4 text-primary" />
                          <h4 className="text-xs font-bold text-foreground group-hover:text-primary transition-colors">{conn.name}</h4>
                        </div>
                        <Badge variant={conn.status === 'CONNECTED' ? 'success' : 'outline'} size="sm">
                          {conn.status}
                        </Badge>
                      </div>
                      <div className="text-[11px] text-muted-foreground font-mono flex justify-between">
                        <span>{conn.host}:{conn.port}</span>
                        <span>{conn.databaseName}</span>
                      </div>
                    </div>
                  ))
                )}
              </CardContent>
            </Card>

            <div className="p-4 rounded-xl bg-muted/40 border border-border space-y-2 text-xs">
              <span className="font-bold text-foreground flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-emerald-500" />
                Enterprise Security Note
              </span>
              <p className="text-muted-foreground leading-relaxed">
                BusinessLens AI requires read-only database permissions. All queries executed by the AI engine or SQL Playground are wrapped in strict read-only transactions.
              </p>
            </div>
          </div>
        </div>
      ) : (
        /* File Upload Tab */
        <Card className="max-w-3xl mx-auto">
          <CardHeader className="pb-4 border-b border-border">
            <CardTitle className="text-base">Upload Flat Spreadsheet (CSV / Excel)</CardTitle>
            <CardDescription>Drag and drop local sales, inventory, or financial data files to analyze.</CardDescription>
          </CardHeader>
          <CardContent className="pt-6 space-y-6">
            <div
              onDragOver={(e) => {
                e.preventDefault();
                setIsDragging(true);
              }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleFileDrop}
              className={`border-2 border-dashed rounded-2xl p-10 text-center transition-all duration-200 ${
                isDragging
                  ? 'border-primary bg-primary/10 scale-[1.01]'
                  : 'border-border bg-muted/30 hover:bg-muted/50 hover:border-primary/50'
              }`}
            >
              <div className="w-16 h-16 rounded-full bg-primary/10 text-primary flex items-center justify-center mx-auto mb-4 shadow-inner">
                <FileSpreadsheet className="w-8 h-8" />
              </div>
              <h3 className="text-base font-bold text-foreground mb-1">Drag and drop your spreadsheet here</h3>
              <p className="text-xs text-muted-foreground mb-6">Supports .CSV, .XLSX, and .XLS files up to 50MB</p>

              <label className="inline-flex items-center justify-center px-4 py-2 rounded-md bg-primary text-primary-foreground text-xs font-semibold cursor-pointer hover:bg-primary/90 shadow-sm transition-all">
                <Upload className="w-4 h-4 mr-2" />
                Browse Local Files
                <input
                  type="file"
                  accept=".csv,.xlsx,.xls"
                  onChange={(e) => {
                    if (e.target.files && e.target.files[0]) {
                      processFile(e.target.files[0]);
                    }
                  }}
                  className="hidden"
                />
              </label>
            </div>

            {selectedFile && (
              <div className="p-4 rounded-xl border border-border bg-card space-y-4 animate-in fade-in-50">
                <div className="flex items-center justify-between pb-3 border-b border-border">
                  <div className="flex items-center gap-3">
                    <FileSpreadsheet className="w-6 h-6 text-emerald-500" />
                    <div>
                      <h4 className="text-sm font-bold text-foreground">{selectedFile.name}</h4>
                      <span className="text-xs text-muted-foreground">{(selectedFile.size / 1024).toFixed(1)} KB • Parsed Successfully</span>
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      setSelectedFile(null);
                      setFilePreview(null);
                    }}
                    className="p-1 rounded text-muted-foreground hover:text-destructive transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                {filePreview && (
                  <div className="space-y-2">
                    <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                      Sample Data Preview (First 10 Rows)
                    </span>
                    <div className="rounded-lg border border-border overflow-x-auto max-h-60">
                      <table className="w-full text-left text-xs">
                        <thead className="bg-muted border-b border-border text-muted-foreground">
                          <tr>
                            {filePreview.columns.map((col, idx) => (
                              <th key={idx} className="p-2.5 font-semibold whitespace-nowrap">
                                {col}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-border bg-card">
                          {filePreview.rows.map((row, rIdx) => (
                            <tr key={rIdx} className="hover:bg-muted/20">
                              {filePreview.columns.map((col, cIdx) => (
                                <td key={cIdx} className="p-2.5 whitespace-nowrap text-foreground font-mono">
                                  {String(row[col] ?? '')}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                <div className="flex justify-end pt-2">
                  <Button
                    variant="primary"
                    size="md"
                    onClick={onConfirmFileUpload}
                    isLoading={isUploading}
                    rightIcon={<ArrowRight className="w-4 h-4" />}
                  >
                    Import Dataset & Start Scan
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};
