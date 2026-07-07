/**
 * Universal Explainability Framework types (Backend V3 Service)
 */

export type ExplainTargetType = 
  | 'KPI'
  | 'DASHBOARD'
  | 'WIDGET'
  | 'AI_INSIGHT'
  | 'FORECAST'
  | 'BUSINESS_RULE'
  | 'RECOMMENDATION'
  | 'MAPPING';

export type AICostSource = 
  | 'BUSINESS_RULES' // No AI cost incurred
  | 'KPI_ENGINE'     // No AI cost incurred
  | 'SEMANTIC_LAYER' // No AI cost incurred
  | 'AI_SUMMARY'     // AI cost incurred
  | 'NONE';

export interface ExplainabilityPayload {
  targetId: string;
  targetType: ExplainTargetType;
  title: string;
  sourceTables: string[];
  sourceColumns: string[];
  formula?: string;
  aggregation?: string;
  appliedFilters: Record<string, unknown>;
  generatedSql?: string; // Permission controlled (only for Data Analyst/Admin)
  businessRulesUsed: string[];
  semanticLayerInfo?: {
    businessField: string;
    mappedColumn: string;
    description: string;
  };
  aiSummary?: string;
  confidence: number; // Percentage 0 - 100
  aiCostSource: AICostSource;
}
