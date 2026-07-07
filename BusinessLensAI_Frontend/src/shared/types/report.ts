/**
 * Report Generation and Export types
 */

export type ReportFormat = 'PDF' | 'EXCEL' | 'CSV';

export type ReportStatus = 'GENERATING' | 'READY' | 'FAILED';

export interface ReportJob {
  id: string;
  title: string;
  sourceDashboardId: string;
  sourceDashboardTitle: string;
  format: ReportFormat;
  status: ReportStatus;
  createdAt: string;
  completedAt?: string;
  downloadUrl?: string;
  errorMessage?: string;
  fileSizeKb?: number;
}

export interface ScheduledReport {
  id: string;
  title: string;
  sourceDashboardId: string;
  format: ReportFormat;
  frequency: 'DAILY' | 'WEEKLY' | 'MONTHLY';
  recipients: string[];
  isEnabled: boolean; // Marked as "Coming Soon" in UI slot
  nextRunAt: string;
}
