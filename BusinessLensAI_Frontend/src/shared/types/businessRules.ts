/**
 * Business Rules Engine types (Backend V3 Service)
 */

export type RuleSeverity = 'CRITICAL' | 'WARNING' | 'INFO';

export type AlertType = 
  | 'REVENUE_DROP'
  | 'NEGATIVE_PROFIT'
  | 'LOW_INVENTORY'
  | 'SALES_SPIKE'
  | 'MISSING_INVENTORY'
  | 'ABNORMAL_DISCOUNTS';

export interface BusinessRuleAlert {
  id: string;
  alertType: AlertType;
  title: string;
  severity: RuleSeverity;
  explanation: string;
  triggerTimestamp: string;
  metricAffected: string;
  currentValue: number | string;
  thresholdValue: number | string;
  isResolved: boolean;
  relatedWidgetId?: string;
}

export interface BusinessRule {
  id: string;
  name: string;
  targetMetric: string;
  condition: 'LESS_THAN' | 'GREATER_THAN' | 'EQUALS' | 'OUTSIDE_RANGE';
  thresholdValue: number;
  severity: RuleSeverity;
  notificationDestination: string;
  isActive: boolean;
}
