import React from 'react';
import { Sparkles, Cpu, CheckCircle2, DollarSign } from 'lucide-react';
import { Badge } from './Badge';
import { AICostSource } from '@/shared/types';

export interface AICostTransparencyBadgeProps {
  source: AICostSource;
  className?: string;
}

export const AICostTransparencyBadge: React.FC<AICostTransparencyBadgeProps> = ({ source, className }) => {
  if (source === 'NONE') return null;

  const isAiUsed = source === 'AI_SUMMARY';

  const sourceLabels: Record<AICostSource, string> = {
    BUSINESS_RULES: 'Business Rules Engine',
    KPI_ENGINE: 'KPI Engine Calculation',
    SEMANTIC_LAYER: 'Semantic Layer Direct',
    AI_SUMMARY: 'LLM AI Synthesis',
    NONE: 'Direct Query',
  };

  return (
    <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border border-border bg-card/60 backdrop-blur-sm text-xs ${className || ''}`}>
      <div className="flex items-center gap-1.5">
        {isAiUsed ? (
          <Sparkles className="w-3.5 h-3.5 text-purple-500 animate-pulse" />
        ) : (
          <Cpu className="w-3.5 h-3.5 text-emerald-500" />
        )}
        <span className="font-semibold text-foreground">Generated using:</span>
        <Badge variant={isAiUsed ? 'purple' : 'success'} size="sm">
          {sourceLabels[source] || source}
        </Badge>
      </div>

      {!isAiUsed && (
        <div className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400 font-medium ml-1">
          <CheckCircle2 className="w-3 h-3" />
          <span>No AI call required ($0.00 cost)</span>
        </div>
      )}

      {isAiUsed && (
        <div className="flex items-center gap-1 text-purple-600 dark:text-purple-400 font-medium ml-1">
          <DollarSign className="w-3 h-3" />
          <span>Optimized AI summary</span>
        </div>
      )}
    </div>
  );
};
