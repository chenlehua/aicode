/** Component for displaying query results in a table. */

import { Table, Tag, Alert, Spin, Skeleton, Button, message } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import type { QueryResult } from '../types';

interface ResultsTableProps {
  result: QueryResult | null;
  loading?: boolean;
}

// Export utilities
const exportToCSV = (result: QueryResult) => {
  const headers = result.columns.map(col => col.name);
  const rows = result.rows.map(row => 
    result.columns.map((_, idx) => {
      const value = row[idx];
      if (value === null) return '';
      if (typeof value === 'string' && (value.includes(',') || value.includes('"') || value.includes('\n'))) {
        return `"${value.replace(/"/g, '""')}"`;
      }
      return String(value);
    }).join(',')
  );
  const csv = [headers.join(','), ...rows].join('\n');
  downloadFile(csv, 'query_results.csv', 'text/csv');
  message.success('CSV exported successfully');
};

const exportToJSON = (result: QueryResult) => {
  const data = result.rows.map(row => {
    const obj: Record<string, unknown> = {};
    result.columns.forEach((col, idx) => {
      obj[col.name] = row[idx];
    });
    return obj;
  });
  const json = JSON.stringify(data, null, 2);
  downloadFile(json, 'query_results.json', 'application/json');
  message.success('JSON exported successfully');
};

const downloadFile = (content: string, filename: string, mimeType: string) => {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

export function ResultsTable({ result, loading }: ResultsTableProps) {
  if (loading) {
    return (
      <div className="p-4">
        <div className="flex items-center justify-center gap-2 mb-4">
          <Spin size="small" />
          <span className="text-gray-500">Executing query...</span>
        </div>
        <Skeleton active paragraph={{ rows: 5 }} />
      </div>
    );
  }

  if (!result) {
    return (
      <div className="p-4">
        <div className="border-b border-gray-200 pb-3 mb-4">
          <span className="text-sm font-semibold text-gray-700 uppercase">RESULTS</span>
        </div>
        <Alert
          message="No Results"
          description="Execute a query to see results here"
          type="info"
          showIcon
        />
      </div>
    );
  }

  if (result.rowCount === 0) {
    return (
      <div className="p-4">
        <div className="border-b border-gray-200 pb-3 mb-4 flex justify-between items-center">
          <span className="text-sm font-semibold text-gray-700 uppercase">
            RESULTS - 0 ROWS - {result.executionTimeMs}MS
          </span>
        </div>
        <Alert
          message="No Rows"
          description="Query executed successfully but returned no rows"
          type="info"
          showIcon
        />
      </div>
    );
  }

  const columns = result.columns.map((col, index) => ({
    title: (
      <span className="font-semibold text-gray-700 uppercase text-xs">{col.name}</span>
    ),
    dataIndex: index,
    key: col.name,
    render: (value: unknown) => {
      if (value === null) {
        return <span className="text-gray-400 italic">NULL</span>;
      }
      if (typeof value === 'boolean') {
        return <Tag color={value ? 'green' : 'red'}>{String(value)}</Tag>;
      }
      if (typeof value === 'object') {
        return (
          <pre className="text-xs bg-gray-50 p-1 rounded">{JSON.stringify(value, null, 2)}</pre>
        );
      }
      return <span className="font-mono text-sm">{String(value)}</span>;
    },
  }));

  const dataSource = result.rows.map((row, index) => ({
    key: index,
    ...row,
  }));

  return (
    <div className="h-full flex flex-col">
      {/* Results Header */}
      <div className="px-4 py-3 border-b border-gray-200 flex justify-between items-center bg-white">
        <span className="text-sm font-semibold text-gray-700 uppercase">
          RESULTS - {result.rowCount} ROWS - {result.executionTimeMs}MS
        </span>
        <div className="flex gap-2">
          <Button
            size="small"
            icon={<DownloadOutlined />}
            onClick={() => exportToCSV(result)}
            className="font-semibold text-xs"
          >
            EXPORT CSV
          </Button>
          <Button
            size="small"
            icon={<DownloadOutlined />}
            onClick={() => exportToJSON(result)}
            className="font-semibold text-xs"
          >
            EXPORT JSON
          </Button>
        </div>
      </div>

      {/* Truncation Warning */}
      {result.truncated && (
        <div className="px-4 py-2 bg-orange-50 border-b border-orange-200">
          <span className="text-xs text-orange-700">Results truncated (max 1000 rows)</span>
        </div>
      )}

      {/* Table */}
      <div className="flex-1 overflow-auto">
        <Table
          columns={columns}
          dataSource={dataSource}
          pagination={{
            pageSize: 50,
            showSizeChanger: true,
            showTotal: (total) => `Total ${total} rows`,
            pageSizeOptions: ['10', '25', '50', '100'],
            className: 'px-4 py-2',
          }}
          scroll={{ x: 'max-content' }}
          size="small"
          className="results-table"
        />
      </div>
    </div>
  );
}
