/**
 * Database and File Connection types (Backend V3 Aligned)
 */

export type DBType = 
  | 'POSTGRESQL'  // Version 1 Officially Supported Production Connector
  | 'MYSQL'       // Future Ready
  | 'SQL_SERVER'  // Future Ready
  | 'ORACLE'      // Future Ready
  | 'SQLITE'      // Future Ready
  | 'FILE_UPLOAD';

export type ConnectionStatus = 'CONNECTED' | 'DISCONNECTED' | 'TESTING' | 'ERROR' | 'SCANNING';

export interface DatabaseConnection {
  id: string;
  name: string;
  type: DBType;
  host?: string;
  port?: number;
  databaseName?: string;
  username?: string;
  status: ConnectionStatus;
  lastConnectedAt?: string;
  errorMessage?: string;
  isProductionReady: boolean; // True for Postgres, False/Disabled for future connectors in V1
  schemaVersion?: string;
  tableCount?: number;
}

export interface DBConnectionFormValues {
  name: string;
  type: DBType;
  host: string;
  port: number;
  databaseName: string;
  username: string;
  password?: string;
}

export interface FileUploadMetadata {
  fileName: string;
  fileSize: number;
  fileType: 'CSV' | 'EXCEL';
  rowCount: number;
  columnCount: number;
  previewRows: Record<string, unknown>[];
}

export type DataType = 'STRING' | 'INTEGER' | 'DECIMAL' | 'BOOLEAN' | 'DATE' | 'TIMESTAMP' | 'JSON';

export interface ColumnMetadata {
  id: string;
  name: string;
  dataType: DataType;
  isPrimaryKey: boolean;
  isForeignKey: boolean;
  foreignKeyRef?: {
    table: string;
    column: string;
  };
  isNullable: boolean;
  sampleValues: unknown[];
  confidenceScore?: number; // AI detection confidence
}

export interface TableMetadata {
  id: string;
  name: string;
  description?: string;
  rowCount: number;
  columns: ColumnMetadata[];
  isAccessible: boolean;
  permissionError?: string;
}

export interface SchemaTree {
  connectionId: string;
  connectionName: string;
  scannedAt: string;
  tables: TableMetadata[];
  totalTables: number;
  scannedTables: number;
  status: 'IN_PROGRESS' | 'COMPLETED' | 'PARTIAL_FAILURE' | 'FAILED';
}
