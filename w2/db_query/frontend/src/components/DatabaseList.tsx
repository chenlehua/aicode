/** Component displaying list of saved database connections. */

import { useState } from 'react';
import { Card, List, Button, Empty, Skeleton, message } from 'antd';
import { DeleteOutlined, DatabaseOutlined } from '@ant-design/icons';
import { useDatabases } from '../hooks/useDatabases';
import { apiFetch } from '../services/api';
import type { Database } from '../types';

interface DatabaseListProps {
  onSelect?: (database: Database) => void;
}

export function DatabaseList({ onSelect }: DatabaseListProps) {
  const { data: databases, isLoading } = useDatabases();
  const [deleting, setDeleting] = useState<string | null>(null);

  const handleDelete = async (name: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm(`Are you sure you want to delete database "${name}"?`)) {
      setDeleting(name);
      try {
        await apiFetch(`/dbs/${name}`, { method: 'DELETE' });
        message.success(`Database "${name}" deleted successfully`);
        // Refetch databases
        window.location.reload();
      } catch (error) {
        message.error(`Failed to delete database "${name}"`);
        setDeleting(null);
      }
    }
  };

  if (isLoading) {
    return (
      <Card>
        <Skeleton active paragraph={{ rows: 3 }} />
      </Card>
    );
  }

  if (!databases || databases.length === 0) {
    return (
      <Card>
        <Empty description="No databases configured" image={Empty.PRESENTED_IMAGE_SIMPLE} />
      </Card>
    );
  }

  return (
    <Card title="Saved Databases">
      <List
        dataSource={databases}
        renderItem={(db) => (
          <List.Item
            className="cursor-pointer hover:bg-gray-50"
            onClick={() => onSelect?.(db)}
            actions={[
              <Button
                key="delete"
                type="text"
                danger
                icon={<DeleteOutlined />}
                onClick={(e) => handleDelete(db.name, e)}
                loading={deleting === db.name}
              />,
            ]}
          >
            <List.Item.Meta
              avatar={<DatabaseOutlined className="text-2xl" />}
              title={db.name}
              description={
                <div className="text-xs text-gray-500 font-mono">
                  {db.url.replace(/:[^:@]+@/, ':****@')}
                </div>
              }
            />
          </List.Item>
        )}
      />
    </Card>
  );
}
