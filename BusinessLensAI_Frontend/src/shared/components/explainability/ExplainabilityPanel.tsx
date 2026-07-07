import React, { useEffect, useState } from 'react';
import { Sparkles, Database, Code2, ShieldAlert, CheckCircle2, Layers, BookOpen, AlertTriangle } from 'lucide-react';
import { Drawer } from '../ui/Drawer';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { LoadingState } from '../ui/LoadingState';
import { AICostTransparencyBadge } from '../ui/AICostTransparencyBadge';
import { usePermission } from '../../hooks/usePermission';
import { explainabilityService } from '../../lib/services/explainabilityService';
import { ExplainabilityPayload, ExplainTargetType } from '@/shared/types';

export interface ExplainabilityPanelProps {
  isOpen: boolean;
  onClose: () => void;
  targetId?: string;
  targetType?: ExplainTargetType;
  title?: string;
}

export const ExplainabilityPanel: React.FC<ExplainabilityPanelProps> = ({
  isOpen,
  onClose,
  targetId = 'exp_default',
  targetType = 'KPI',
  title = 'Universal Explainability Analysis',
}) => {
  const [data, setData] = useState<ExplainabilityPayload | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { can } = usePermission();

  const canViewSql = can('view_sql_reasoning');

  useEffect(() => {
    if (!isOpen || !targetId) return;
    setIsLoading(true);
    setError(null);
    explainabilityService
      .getExplanation(targetType, targetId)
      .then((res) => {
        setData(res);
        setIsLoading(false);
      })
      .catch((err) => {
        setError(err.message || 'Failed to fetch explainability metadata.');
        setIsLoading(false);
      });
  }, [isOpen, targetId, targetType]);

  return (
    <Drawer
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      description={`Transparency report for ${targetType} artifact (${targetId})`}
      size="lg"
    >
      {isLoading && <LoadingState type="list" count={4} message="Analyzing semantic lineage and business rules..." />}

      {error && (
        <div className="p-6 rounded-xl bg-destructive/10 border border-destructive/20 text-center space-y-3">
          <AlertTriangle className="w-8 h-8 text-destructive mx-auto" />
          <h4 className="font-semibold text-foreground">Explainability Error</h4>
          <p className="text-xs text-muted-foreground">{error}</p>
          <Button variant="outline" size="sm" onClick={() => setIsLoading(true)}>
            Retry Analysis
          </Button>
        </div>
      )}

      {!isLoading && !error && data && (
        <div className="space-y-6 animate-in fade-in-50 duration-200">
          {/* Top Banner: Confidence & AI Cost */}
          <div className="p-4 rounded-xl bg-card border border-border space-y-3 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Confidence Score</span>
              <Badge variant={data.confidence >= 90 ? 'success' : 'warning'} size="md">
                {data.confidence}% Verified
              </Badge>
            </div>
            <div className="h-2 w-full rounded-full bg-muted overflow-hidden">
              <div
                className={`h-full transition-all duration-500 ${data.confidence >= 90 ? 'bg-emerald-500' : 'bg-amber-500'}`}
                style={{ width: `${data.confidence}%` }}
              />
            </div>
            <div className="pt-2 border-t border-border">
              <AICostTransparencyBadge source={data.aiCostSource} />
            </div>
          </div>

          {/* AI Summary */}
          {data.aiSummary && (
            <div className="p-4 rounded-xl bg-purple-500/5 border border-purple-500/20 space-y-2">
              <div className="flex items-center gap-2 text-xs font-semibold text-purple-600 dark:text-purple-400 uppercase tracking-wider">
                <Sparkles className="w-4 h-4" />
                <span>AI Synthesis & Audit Summary</span>
              </div>
              <p className="text-sm text-foreground leading-relaxed">{data.aiSummary}</p>
            </div>
          )}

          {/* Semantic Layer Information */}
          {data.semanticLayerInfo && (
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-xs font-semibold text-foreground uppercase tracking-wider">
                <Layers className="w-4 h-4 text-blue-500" />
                <span>Semantic Layer Mapping</span>
              </div>
              <div className="p-4 rounded-xl bg-card border border-border space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Business Concept:</span>
                  <span className="font-semibold text-primary">{data.semanticLayerInfo.businessField}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Physical Column:</span>
                  <span className="font-mono text-foreground">{data.semanticLayerInfo.mappedColumn}</span>
                </div>
                <div className="pt-2 border-t border-border text-muted-foreground leading-relaxed">
                  {data.semanticLayerInfo.description}
                </div>
              </div>
            </div>
          )}

          {/* Generated SQL (Permission Controlled) */}
          <div className="space-y-2 pt-2 border-t border-border">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-semibold text-foreground uppercase tracking-wider">
                <Code2 className="w-4 h-4 text-primary" />
                <span>Generated SQL Query</span>
              </div>
              {!canViewSql && (
                <Badge variant="warning" size="sm">
                  Role Restricted
                </Badge>
              )}
            </div>

            {canViewSql ? (
              <div className="relative rounded-xl overflow-hidden border border-border bg-slate-950 p-4">
                <pre className="text-xs font-mono text-emerald-400 overflow-x-auto whitespace-pre-wrap leading-relaxed">
                  {data.generatedSql || '-- No SQL query generated for this artifact.'}
                </pre>
              </div>
            ) : (
              <div className="p-6 rounded-xl bg-muted/40 border border-dashed border-border text-center space-y-2">
                <ShieldAlert className="w-8 h-8 text-amber-500 mx-auto" />
                <h5 className="text-sm font-semibold text-foreground">SQL Lineage Restricted</h5>
                <p className="text-xs text-muted-foreground max-w-sm mx-auto leading-relaxed">
                  Raw SQL execution and query inspection are restricted to Data Analysts and Administrators.
                </p>
              </div>
            )}
          </div>

          <div className="flex justify-end pt-4 border-t border-border">
            <Button variant="outline" onClick={onClose}>
              Close Explanation
            </Button>
          </div>
        </div>
      )}
    </Drawer>
  );
};
