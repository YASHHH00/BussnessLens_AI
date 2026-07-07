import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Sparkles, Calculator, CheckCircle2, ArrowRight } from 'lucide-react';
import { Button, Input, Card, CardHeader, CardTitle, CardDescription, CardContent, Badge, LoadingState, ExplainabilityPanel, DomainSelector } from '../../shared/components';
import { semanticService } from '../../shared/lib/services/semanticService';
import { SemanticField } from '../../shared/types';
import { useAppStore } from '../../shared/stores/useAppStore';

export const SemanticExplorerPage: React.FC = () => {
  const navigate = useNavigate();
  const setWorkflowStep = useAppStore((s) => s.setWorkflowStep);

  const [fields, setFields] = useState<SemanticField[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [searchTerm, setSearchTerm] = useState<string>('');

  // Explainability Panel State
  const [explainModalOpen, setExplainModalOpen] = useState<boolean>(false);
  const [selectedFieldId, setSelectedFieldId] = useState<string | null>(null);
  const [selectedFieldTitle, setSelectedFieldTitle] = useState<string>('');

  useEffect(() => {
    setIsLoading(true);
    semanticService
      .getSemanticFields('conn_pg_01')
      .then((data) => {
        setFields(data);
        setIsLoading(false);
      })
      .catch(() => setIsLoading(false));
  }, []);

  const filteredFields = fields.filter(
    (f) =>
      f.businessField.toLowerCase().includes(searchTerm.toLowerCase()) ||
      f.displayName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      f.mappedColumn.toLowerCase().includes(searchTerm.toLowerCase()) ||
      f.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const openExplainability = (field: SemanticField) => {
    setSelectedFieldId(field.id);
    setSelectedFieldTitle(`Semantic Concept: ${field.businessField}`);
    setExplainModalOpen(true);
  };

  const onProceedToRecommendations = () => {
    setWorkflowStep('RECOMMENDED_DASHBOARDS');
    navigate('/recommendations');
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto animate-in fade-in-50 duration-300 pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Badge variant="purple">Step 5: Semantic Layer (Backend V3)</Badge>
            <DomainSelector />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">Semantic Layer Explorer</h1>
          <p className="text-sm text-muted-foreground">
            Explore how business concepts, mathematical KPI formulas, and aggregation rules map to physical database tables.
          </p>
        </div>

        <Button
          variant="primary"
          size="md"
          onClick={onProceedToRecommendations}
          rightIcon={<ArrowRight className="w-4 h-4" />}
        >
          View Dashboard Recommendations
        </Button>
      </div>

      {/* Top Search Bar & Stats */}
      <Card className="bg-muted/20 border-border">
        <CardContent className="p-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="w-full sm:max-w-md">
            <Input
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by business concept, table, or column name..."
              leftIcon={<Search className="w-4 h-4 text-muted-foreground" />}
              className="h-10 text-xs bg-background"
            />
          </div>
          <div className="flex items-center gap-4 text-xs text-muted-foreground whitespace-nowrap">
            <span>
              Showing <strong className="text-foreground">{filteredFields.length}</strong> of <strong className="text-foreground">{fields.length}</strong> semantic concepts
            </span>
            <Badge variant="success" className="hidden md:inline-flex">
              100% Verified
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Semantic Concepts Grid */}
      {isLoading ? (
        <LoadingState type="card" count={4} message="Loading semantic lineage definitions..." />
      ) : filteredFields.length === 0 ? (
        <div className="p-12 text-center rounded-xl border border-dashed border-border bg-card/40">
          <p className="text-sm text-muted-foreground">No semantic concepts matched your search query.</p>
          <Button variant="ghost" size="sm" onClick={() => setSearchTerm('')} className="mt-2 text-xs">
            Clear Search Filter
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredFields.map((field) => (
            <Card key={field.id} hoverEffect className="flex flex-col justify-between border-border/80">
              <CardHeader className="pb-4 border-b border-border">
                <div className="flex items-start justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <CardTitle className="text-lg font-bold text-foreground">{field.businessField}</CardTitle>
                      {field.isForecastable && (
                        <Badge variant="purple" size="sm">
                          Forecastable
                        </Badge>
                      )}
                    </div>
                    <span className="text-xs font-semibold text-primary">{field.displayName}</span>
                  </div>
                  <Badge variant={field.currentStatus === 'MAPPED' ? 'success' : 'warning'} size="sm">
                    {field.currentStatus}
                  </Badge>
                </div>
                <CardDescription className="pt-2 leading-relaxed">{field.description}</CardDescription>
              </CardHeader>

              <CardContent className="p-6 space-y-4 flex-1 flex flex-col justify-between">
                <div className="space-y-3">
                  {/* Physical Lineage */}
                  <div className="p-3 rounded-xl bg-muted/40 border border-border space-y-2 text-xs">
                    <div className="flex justify-between items-center">
                      <span className="text-muted-foreground font-semibold">Physical Source:</span>
                      <span className="font-mono font-bold text-foreground">
                        {field.mappedTable}.{field.mappedColumn}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-muted-foreground font-semibold">Data Type & Aggregation:</span>
                      <div className="flex items-center gap-1.5">
                        <Badge variant="outline" size="sm" className="font-mono">
                          {field.dataType}
                        </Badge>
                        <Badge variant="info" size="sm">
                          {field.aggregation}
                        </Badge>
                      </div>
                    </div>
                  </div>

                  {/* Formula Box */}
                  {field.formula && (
                    <div className="space-y-1">
                      <span className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider flex items-center gap-1">
                        <Calculator className="w-3.5 h-3.5 text-primary" />
                        Mathematical Formula
                      </span>
                      <div className="p-2.5 rounded-lg bg-background border border-border font-mono text-xs font-bold text-primary truncate" title={field.formula}>
                        {field.formula}
                      </div>
                    </div>
                  )}

                  {/* Sample Values Preview */}
                  {field.sampleValues && field.sampleValues.length > 0 && (
                    <div className="space-y-1">
                      <span className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">
                        Live Sample Data
                      </span>
                      <div className="p-2 rounded-lg bg-muted/30 font-mono text-xs text-muted-foreground truncate">
                        {field.sampleValues.join(', ')}
                      </div>
                    </div>
                  )}
                </div>

                {/* Footer actions */}
                <div className="pt-4 border-t border-border flex items-center justify-between">
                  <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    {field.confidence}% Confidence
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => openExplainability(field)}
                    leftIcon={<Sparkles className="w-3.5 h-3.5 text-purple-500" />}
                    className="h-8 text-xs font-semibold"
                  >
                    Inspect Explainability
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Universal Explainability Panel */}
      <ExplainabilityPanel
        isOpen={explainModalOpen}
        onClose={() => setExplainModalOpen(false)}
        targetId={selectedFieldId || 'sem_01'}
        targetType="MAPPING"
        title={selectedFieldTitle}
      />

      {/* Bottom CTA */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-card to-purple-500/10 border border-border flex flex-col sm:flex-row items-center justify-between gap-4 shadow-sm">
        <div className="space-y-1">
          <h3 className="text-base font-bold text-foreground flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-purple-500" />
            <span>Semantic Layer Ready</span>
          </h3>
          <p className="text-xs text-muted-foreground">
            The AI engine has compiled your domain mappings. Generate tailored dashboards and KPI cards next!
          </p>
        </div>
        <Button
          variant="primary"
          size="lg"
          onClick={onProceedToRecommendations}
          rightIcon={<ArrowRight className="w-4 h-4" />}
          className="w-full sm:w-auto font-bold"
        >
          Continue to Step 6: Recommendations
        </Button>
      </div>
    </div>
  );
};
