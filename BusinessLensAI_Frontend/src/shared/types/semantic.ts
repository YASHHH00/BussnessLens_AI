/**
 * Semantic Layer types (Backend V3 Service)
 */

export type SemanticDomain = 
  | 'RETAIL'         // Version 1 Supported
  | 'FOOD_DELIVERY'  // Future Plugin
  | 'WAREHOUSE'      // Future Plugin
  | 'RIDE_SHARING'   // Future Plugin
  | 'HEALTHCARE';    // Future Plugin

export type AggregationType = 'SUM' | 'AVG' | 'COUNT' | 'COUNT_DISTINCT' | 'MIN' | 'MAX' | 'NONE';

export interface SemanticField {
  id: string;
  businessField: string;
  displayName: string;
  mappedTable: string;
  mappedColumn: string;
  aggregation: AggregationType;
  formula?: string; // Mathematical formula if calculated e.g. "Profit / Revenue * 100"
  dataType: 'STRING' | 'NUMERIC' | 'DATE' | 'BOOLEAN';
  isForecastable: boolean;
  description: string;
  currentStatus: 'MAPPED' | 'UNMAPPED' | 'DRIFTED' | 'UNDER_REVIEW';
  sampleValues: unknown[];
  confidence: number;
}

export interface SemanticModel {
  domain: SemanticDomain;
  connectionId: string;
  fields: SemanticField[];
  lastUpdated: string;
  version: string;
}
