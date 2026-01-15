/** Component displaying list of saved database connections. */

import { useState } from 'react';
import { Card, List, Button, Empty, Skeleton, message, Typography, Tag } from 'antd';
import { DeleteOutlined, DatabaseOutlined, RightOutlined } from '@ant-design/icons';
import { useDatabases } from '../hooks/useDatabases';
import { apiFetch } from '../services/api';
import type { Database } from '../types';

const { Text } = Typography;

interface DatabaseListProps {
  onSelect?: (database: Database) => void;
}

export function DatabaseList({ onSelect }: DatabaseListProps) {
  const { data: databases, isLoading } = useDatabases();
  const [deleting, setDeleting] = useState<string | null>(null);

  const handleDelete = async (name: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm(`确定要删除数据库连接 "${name}" 吗？`)) {
      setDeleting(name);
      try {
        await apiFetch(`/dbs/${name}`, { method: 'DELETE' });
        message.success(`数据库连接 "${name}" 删除成功`);
        // Refetch databases
        window.location.reload();
      } catch (error) {
        message.error(`删除数据库连接 "${name}" 失败`);
        setDeleting(null);
      }
    }
  };

  if (isLoading) {
    return (
      <Card className="rounded-xl shadow-sm border-0">
        <Skeleton active paragraph={{ rows: 3 }} />
      </Card>
    );
  }

  if (!databases || databases.length === 0) {
    return (
      <Card className="rounded-xl shadow-sm border-0">
        <Empty
          description={
            <Text className="text-gray-500">暂无数据库连接，点击上方按钮添加</Text>
          }
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          className="py-12"
        />
      </Card>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {databases.map((db) => (
        <Card
          key={db.name}
          className="rounded-xl shadow-sm hover:shadow-md transition-all duration-200 border-0 cursor-pointer group"
          onClick={() => onSelect?.(db)}
          actions={[
            <Button
              key="delete"
              type="text"
              danger
              icon={<DeleteOutlined />}
              onClick={(e) => handleDelete(db.name, e)}
              loading={deleting === db.name}
              className="opacity-0 group-hover:opacity-100 transition-opacity"
            />,
          ]}
        >
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-100 to-blue-200 flex items-center justify-center flex-shrink-0 group-hover:from-blue-200 group-hover:to-blue-300 transition-colors">
              <DatabaseOutlined className="text-xl text-blue-600" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-2">
                <Text strong className="text-base text-gray-800 block truncate">
                  {db.name}
                </Text>
                <RightOutlined className="text-gray-400 group-hover:text-blue-500 transition-colors" />
              </div>
              <Text className="text-xs text-gray-500 font-mono block truncate">
                {db.url.replace(/:[^:@]+@/, ':****@')}
              </Text>
              <div className="mt-3">
                <Tag color="blue" className="rounded-md">
                  PostgreSQL
                </Tag>
              </div>
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}
