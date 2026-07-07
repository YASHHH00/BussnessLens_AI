/**
 * AI Assistant and Natural Language Q&A types (Backend V3 Aligned)
 */

export type ChatRole = 'user' | 'assistant' | 'system';

export interface ReasoningStep {
  stepNumber: number;
  action: string;
  description: string;
  timestamp?: string;
}

export interface ExpandedReasoningTrail {
  businessRulesUsed: string[];
  semanticLayerRefs: string[];
  reasoningSteps: ReasoningStep[];
  generatedSql?: string; // Visible only to Data Analyst and Admin
  confidenceScore: number; // 0 to 100
  aiSummary: string;
}

export interface AIResponsePayload {
  textExplanation: string;
  chartConfig?: {
    type: 'LINE' | 'BAR' | 'PIE' | 'AREA' | 'SCATTER';
    title: string;
    data: Record<string, unknown>[];
    xAxisKey: string;
    yAxisKey: string;
  };
  tableData?: {
    columns: string[];
    rows: Record<string, unknown>[];
  };
  reasoningTrail?: ExpandedReasoningTrail;
  isAmbiguous?: boolean;
  clarifyingQuestion?: string;
}

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  timestamp: string;
  payload?: AIResponsePayload;
  isLoading?: boolean;
  isStreaming?: boolean;
}

export interface SuggestedPrompt {
  id: string;
  text: string;
  category: 'FINANCIAL' | 'OPERATIONAL' | 'FORECASTING' | 'TROUBLESHOOTING';
}
