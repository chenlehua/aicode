/** Component for displaying query results in a table. */

import { Table, Tag, Alert, Spin, Skeleton } from 'antd';
import type { QueryResult } from '../types';

interface ResultsTableProps {
  result: QueryResult | null;
  loading?: boolean;
}

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
      <Alert
        message="No Results"
        description="Execute a query to see results here"
        type="info"
        showIcon
      />
    );
  }

  if (result.rowCount === 0) {
    return (
      <Alert
        message="No Rows"
        description="Query executed successfully but returned no rows"
        type="info"
        showIcon
      />
    );
  }

  const columns = result.columns.map((col, index) => ({
    title: (
      <div>
        <span className="font-semibold">{col.name}</span>
        <Tag color="blue" className="ml-2 text-xs">
          {col.dataType}
        </Tag>
      </div>
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
    <div>
      <div className="mb-2 flex justify-between items-center">
        <div>
          <Tag color="green">{result.rowCount} rows</Tag>
          {result.truncated && <Tag color="orange">Results truncated (max 1000 rows)</Tag>}
          <Tag color="blue">{result.executionTimeMs}ms</Tag>
        </div>
      </div>
      <Table
        columns={columns}
        dataSource={dataSource}
        pagination={{
          pageSize: 50,
          showSizeChanger: true,
          showTotal: (total) => `Total ${total} rows`,
        }}
        scroll={{ x: 'max-content', y: 400 }}
        size="small"
      />
    </div>
  );
}
