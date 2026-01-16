/** Component displaying query execution history. */

import { Card, List, Tag, Button, Empty, Alert, Skeleton, Spin } from 'antd';
import { PlayCircleOutlined, ClockCircleOutlined } from '@ant-design/icons';
import type { QueryHistoryItem } from '../types';

interface QueryHistoryProps {
  items: QueryHistoryItem[];
  onReplay?: (sql: string) => void;
  loading?: boolean;
}

export function QueryHistory({ items, onReplay, loading = false }: QueryHistoryProps) {
  if (loading) {
    return (
      <Card>
        <div className="flex items-center justify-center gap-2 mb-4">
          <Spin size="small" />
          <span className="text-gray-500">Loading history...</span>
        </div>
        <Skeleton active paragraph={{ rows: 3 }} />
      </Card>
    );
  }

  if (items.length === 0) {
    return (
      <Card>
        <Empty description="No query history" image={Empty.PRESENTED_IMAGE_SIMPLE} />
      </Card>
    );
  }

  return (
    <Card title="Query History">
      <List
        dataSource={items}
        renderItem={(item) => (
          <List.Item
            actions={
              onReplay
                ? [
                    <Button
                      key="replay"
                      type="text"
                      icon={<PlayCircleOutlined />}
                      onClick={() => onReplay(item.sql)}
                    >
                      Replay
                    </Button>,
                  ]
                : []
            }
          >
            <List.Item.Meta
              title={
                <div className="flex items-center gap-2">
                  <Tag color={item.status === 'success' ? 'green' : 'red'}>{item.status}</Tag>
                  <Tag>{item.queryType}</Tag>
                  {item.rowCount > 0 && <Tag color="blue">{item.rowCount} rows</Tag>}
                  <Tag>
                    <ClockCircleOutlined /> {item.executionTimeMs}ms
                  </Tag>
                </div>
              }
              description={
                <div>
                  <pre className="text-xs bg-gray-50 p-2 rounded mt-2 overflow-x-auto">
                    {item.sql}
                  </pre>
                  {item.errorMessage && (
                    <Alert message={item.errorMessage} type="error" showIcon className="mt-2" />
                  )}
                  <div className="text-xs text-gray-500 mt-2">
                    {new Date(item.executedAt).toLocaleString()}
                  </div>
                </div>
              }
            />
          </List.Item>
        )}
      />
    </Card>
  );
}
