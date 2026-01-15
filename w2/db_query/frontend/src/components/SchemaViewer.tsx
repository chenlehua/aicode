/** Component displaying database schema (tables, views, columns). */

import { Card, Tabs, Table, Tag, Collapse } from 'antd';
import { TableOutlined, EyeOutlined } from '@ant-design/icons';
import type { DatabaseMetadata, ColumnMetadata } from '../types';

interface SchemaViewerProps {
  metadata: DatabaseMetadata;
}

export function SchemaViewer({ metadata }: SchemaViewerProps) {
  const renderColumns = (columns: ColumnMetadata[]) => {
    const columnsData = columns.map((col) => ({
      key: col.name,
      name: col.name,
      dataType: col.dataType,
      nullable: col.isNullable,
      defaultValue: col.defaultValue,
      primaryKey: col.isPrimaryKey,
      foreignKey: col.isForeignKey,
      references: col.references,
    }));

    return (
      <Table
        dataSource={columnsData}
        pagination={false}
        size="small"
        columns={[
          {
            title: 'Column',
            dataIndex: 'name',
            key: 'name',
            render: (text: string, record: (typeof columnsData)[0]) => (
              <div>
                <span className="font-mono font-semibold">{text}</span>
                {record.primaryKey && (
                  <Tag color="blue" className="ml-2">
                    PK
                  </Tag>
                )}
                {record.foreignKey && (
                  <Tag color="green" className="ml-2">
                    FK
                  </Tag>
                )}
              </div>
            ),
          },
          {
            title: 'Type',
            dataIndex: 'dataType',
            key: 'dataType',
            render: (text: string) => <span className="font-mono text-xs">{text}</span>,
          },
          {
            title: 'Nullable',
            dataIndex: 'nullable',
            key: 'nullable',
            render: (nullable: boolean) => (
              <Tag color={nullable ? 'default' : 'red'}>{nullable ? 'YES' : 'NO'}</Tag>
            ),
          },
          {
            title: 'Default',
            dataIndex: 'defaultValue',
            key: 'defaultValue',
            render: (value: string | undefined) =>
              value ? (
                <span className="font-mono text-xs">{value}</span>
              ) : (
                <span className="text-gray-400">—</span>
              ),
          },
          {
            title: 'References',
            dataIndex: 'references',
            key: 'references',
            render: (value: string | undefined) =>
              value ? (
                <span className="font-mono text-xs">{value}</span>
              ) : (
                <span className="text-gray-400">—</span>
              ),
          },
        ]}
      />
    );
  };

  const tableItems = metadata.tables.map((table) => ({
    key: table.tableName,
    label: (
      <span>
        <TableOutlined className="mr-2" />
        {table.tableName}
      </span>
    ),
    children: (
      <Collapse
        items={[
          {
            key: 'columns',
            label: `Columns (${table.columns.length})`,
            children: renderColumns(table.columns),
          },
        ]}
      />
    ),
  }));

  const viewItems = metadata.views.map((view) => ({
    key: view.tableName,
    label: (
      <span>
        <EyeOutlined className="mr-2" />
        {view.tableName}
      </span>
    ),
    children: (
      <Collapse
        items={[
          {
            key: 'columns',
            label: `Columns (${view.columns.length})`,
            children: renderColumns(view.columns),
          },
        ]}
      />
    ),
  }));

  const tabItems = [
    {
      key: 'tables',
      label: (
        <span>
          Tables <Tag>{metadata.tableCount}</Tag>
        </span>
      ),
      children: <Collapse items={tableItems} defaultActiveKey={[]} size="small" />,
    },
    {
      key: 'views',
      label: (
        <span>
          Views <Tag>{metadata.viewCount}</Tag>
        </span>
      ),
      children: <Collapse items={viewItems} defaultActiveKey={[]} size="small" />,
    },
  ];

  return (
    <Card
      className="rounded-xl shadow-sm border-0"
      title={
        <div className="flex items-center gap-2">
          <span className="text-lg font-semibold">数据库结构</span>
          <span className="text-xs text-gray-500 font-normal">
            ({metadata.tableCount} 表, {metadata.viewCount} 视图)
          </span>
        </div>
      }
      extra={
        <span className="text-xs text-gray-500">
          更新时间: {new Date(metadata.fetchedAt).toLocaleString()}
        </span>
      }
    >
      <Tabs items={tabItems} size="large" />
    </Card>
  );
}
