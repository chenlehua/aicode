/** TypeScript interfaces for DB Query API models. */

export interface Database {
  name: string;
  url: string;
  createdAt: string;
  updatedAt: string;
}

export interface ColumnMetadata {
  name: string;
  dataType: string;
  isNullable: boolean;
  defaultValue?: string;
  isPrimaryKey: boolean;
  isForeignKey: boolean;
  references?: string; // "table.column" format
}

export interface TableMetadata {
  tableName: string;
  tableType: 'table' | 'view';
  columns: ColumnMetadata[];
  fetchedAt: string;
}

export interface DatabaseMetadata {
  databaseName: string;
  tables: TableMetadata[];
  views: TableMetadata[];
  tableCount: number;
  viewCount: number;
  fetchedAt: string;
}

export interface DatabaseWithMetadata extends Database {
  metadata: DatabaseMetadata;
}

export interface QueryRequest {
  sql: string;
}

export interface NaturalQueryRequest {
  prompt: string;
}

export interface ColumnInfo {
  name: string;
  dataType: string;
}

export interface QueryResult {
  columns: ColumnInfo[];
  rows: unknown[][];
  rowCount: number;
  truncated: boolean;
  executionTimeMs: number;
}

export interface GeneratedSQL {
  sql: string;
  explanation?: string;
}

export interface ErrorResponse {
  error: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface QueryHistoryItem {
  id: number;
  databaseName: string;
  sql: string;
  queryType: 'manual' | 'natural';
  naturalPrompt?: string;
  rowCount: number;
  executionTimeMs: number;
  status: 'success' | 'error';
  errorMessage?: string;
  executedAt: string;
}

export interface QueryHistoryList {
  items: QueryHistoryItem[];
  total: number;
  page: number;
  pageSize: number;
}
