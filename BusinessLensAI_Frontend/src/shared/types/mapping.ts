/**
 * AI Schema Mapping and Recommendation types (Backend V3 Aligned)
 */

import { DataType } from './connection';
import { AggregationType } from './semantic';

export type MappingStatus = 'PENDING' | 'CONFIRMED' | 'MODIFIED' | 'ERROR';

export interface BusinessField {
  id: string;
  name: string;
  expectedDataType: DataType;
  required: boolean;
  category: 'REVENUE' | 'DATE' | 'IDENTIFIER' | 'DIMENSION' | 'METRIC';
  description: string;
}

export interface MappingSuggestion {
  businessFieldId: string;
  suggestedColumnId: string;
  suggestedTableName: string;
  suggestedColumnName: string;
  confidenceScore: number; // 0 to 100
  reasoning?: string;
}

export interface ColumnMapping {
  id: string;
  businessFieldId: string;
  businessFieldName: string;
  mappedTableName: string;
  mappedColumnName: string;
  dataType: DataType;
  aggregation: AggregationType;
  sampleValues: unknown[];
  isForecastable: boolean;
  semanticDescription: string;
  confidenceScore: number;
  status: MappingStatus;
  isAiSuggested: boolean;
  validationError?: string;
}

export interface SchemaDriftAlert {
  id: string;
  connectionId: string;
  detectedAt: string;
  affectedMappingsCount: number;
  changes: {
    oldColumnName: string;
    newColumnName?: string;
    tableName: string;
    changeType: 'RENAMED' | 'DELETED' | 'TYPE_CHANGED';
  }[];
}

export interface SuggestedKPI {
  id: string;
  name: string; // e.g., "Revenue", "Profit Margin", "Customer Retention", "Inventory Turnover", "AOV"
  description: string;
  formula: string;
  defaultChartType: 'KPI' | 'LINE' | 'BAR';
  isSelected: boolean;
  category: 'FINANCIAL' | 'OPERATIONAL' | 'CUSTOMER';
}
