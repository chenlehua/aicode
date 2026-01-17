/** Component for displaying query results in a table. */

import { Table, Tag, Alert, Spin, Skeleton, Button, message } from 'antd';
import { DownloadOutlined, FileTextOutlined, CheckCircleOutlined } from '@ant-design/icons';
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
  message.success('CSV 导出成功');
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
  message.success('JSON 导出成功');
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
      <div className="p-6">
        <div className="flex items-center justify-center gap-3 mb-6">
          <Spin size="default" />
          <span className="text-text-secondary font-medium">正在执行查询...</span>
        </div>
        <Skeleton active paragraph={{ rows: 5 }} />
      </div>
    );
  }

  if (!result) {
    return (
      <div className="p-6">
        <div className="border-b border-border-light pb-4 mb-6">
          <span className="text-sm font-semibold text-text-secondary uppercase tracking-wide">
            查询结果
          </span>
        </div>
        <div className="text-center py-12">
          <div className="w-16 h-16 rounded-2xl bg-bg-tertiary flex items-center justify-center mx-auto mb-4">
            <FileTextOutlined className="text-2xl text-text-tertiary" />
          </div>
          <p className="text-text-secondary mb-1">暂无结果</p>
          <p className="text-sm text-text-tertiary">执行查询后在这里查看结果</p>
        </div>
      </div>
    );
  }

  if (result.rowCount === 0) {
    return (
      <div className="p-6">
        <div className="border-b border-border-light pb-4 mb-6 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <span className="text-sm font-semibold text-text-secondary uppercase tracking-wide">
              查询结果
            </span>
            <span className="text-xs px-2.5 py-1 bg-bg-tertiary rounded-full text-text-secondary">
              0 行 · {result.executionTimeMs}ms
            </span>
          </div>
        </div>
        <div className="text-center py-12">
          <div className="w-16 h-16 rounded-2xl bg-accent-green/10 flex items-center justify-center mx-auto mb-4">
            <CheckCircleOutlined className="text-2xl text-accent-green" />
          </div>
          <p className="text-text-secondary mb-1">查询执行成功</p>
          <p className="text-sm text-text-tertiary">查询未返回任何数据行</p>
        </div>
      </div>
    );
  }

  const columns = result.columns.map((col, index) => ({
    title: (
      <span className="font-semibold text-text-secondary uppercase text-xs tracking-wide">
        {col.name}
      </span>
    ),
    dataIndex: index,
    key: col.name,
    render: (value: unknown) => {
      if (value === null) {
        return <span className="text-text-tertiary italic text-sm">NULL</span>;
      }
      if (typeof value === 'boolean') {
        return (
          <Tag color={value ? 'green' : 'red'} className="font-mono">
            {String(value)}
          </Tag>
        );
      }
      if (typeof value === 'object') {
        return (
          <pre className="text-xs bg-bg-tertiary p-2 rounded-lg font-mono max-w-xs overflow-auto">
            {JSON.stringify(value, null, 2)}
          </pre>
        );
      }
      return <span className="font-mono text-sm text-text-primary">{String(value)}</span>;
    },
  }));

  const dataSource = result.rows.map((row, index) => ({
    key: index,
    ...row,
  }));

  return (
    <div className="h-full flex flex-col">
      {/* Results Header */}
      <div className="px-6 py-4 border-b border-border-light flex justify-between items-center bg-white">
        <div className="flex items-center gap-3">
          <span className="text-sm font-semibold text-text-secondary uppercase tracking-wide">
            查询结果
          </span>
          <span className="text-xs px-2.5 py-1 bg-accent-green/10 text-accent-green rounded-full font-medium">
            {result.rowCount} 行
          </span>
          <span className="text-xs px-2.5 py-1 bg-accent-secondary/10 text-accent-secondary rounded-full font-medium">
            {result.executionTimeMs}ms
          </span>
        </div>
        <div className="flex gap-2">
          <Button
            size="small"
            icon={<DownloadOutlined />}
            onClick={() => exportToCSV(result)}
            className="font-medium text-xs"
          >
            CSV
          </Button>
          <Button
            size="small"
            icon={<DownloadOutlined />}
            onClick={() => exportToJSON(result)}
            className="font-medium text-xs"
          >
            JSON
          </Button>
        </div>
      </div>

      {/* Truncation Warning */}
      {result.truncated && (
        <div className="px-6 py-3 bg-warning/10 border-b border-warning/20">
          <span className="text-xs text-warning font-medium">
            ⚠️ 结果已截断（最多显示 1000 行）
          </span>
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
            showTotal: (total) => `共 ${total} 行`,
            pageSizeOptions: ['10', '25', '50', '100'],
            className: 'px-6 py-3',
          }}
          scroll={{ x: 'max-content' }}
          size="small"
          className="results-table"
        />
      </div>
    </div>
  );
}
