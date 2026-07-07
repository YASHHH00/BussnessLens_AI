/**
 * Data Quality Report types (Backend V3 Service)
 */

export type SeverityBadge = 'CRITICAL' | 'WARNING' | 'INFO' | 'PASS';

export interface ConsistencyCheck {
  id: string;
  name: string;
  description: string;
  status: SeverityBadge;
  affectedRows: number;
  recommendation: string;
}

export interface ColumnCompleteness {
  columnName: string;
  tableName: string;
  totalRows: number;
  nullCount: number;
  nullPercentage: number;
  status: SeverityBadge;
}

export interface DataQualityReport {
  connectionId: string;
  overallScore: number; // 0 to 100
  scannedAt: string;
  missingValuesCount: number;
  duplicateRowsCount: number;
  nullPercentage: number;
  invalidDatesCount: number;
  outliersCount: number;
  relationshipIssuesCount: number;
  orphanRecordsCount: number;
  columnCompleteness: ColumnCompleteness[];
  consistencyChecks: ConsistencyCheck[];
  topRecommendations: string[];
  metrics?: {
    completeness: number;
    consistency: number;
    uniqueness: number;
    validity: number;
    [key: string]: unknown;
  };
  issues?: {
    id: string;
    title?: string;
    severity: string;
    tableName: string;
    columnName?: string;
    description: string;
    impact: string;
    affectedRows?: number | string;
    recommendation?: string;
    category?: string;
  }[];
}
