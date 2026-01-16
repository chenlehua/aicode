/** Custom sidebar component with database list and add button. */

import { useState, useMemo } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button, Empty, Skeleton, Modal, message, Typography, Input } from 'antd';
import { PlusOutlined, DeleteOutlined, DatabaseOutlined, SearchOutlined } from '@ant-design/icons';
import { useDatabases } from '../hooks/useDatabases';
import { AddDatabaseForm } from './AddDatabaseForm';
import { apiFetch } from '../services/api';
import type { Database } from '../types';

const { Text } = Typography;

export function CustomSider() {
  const navigate = useNavigate();
  const location = useLocation();
  const { data: databases, isLoading, refetch } = useDatabases();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [searchText, setSearchText] = useState('');

  // Filter databases based on search text
  const filteredDatabases = useMemo(() => {
    if (!databases) return [];
    if (!searchText.trim()) return databases;
    const lower = searchText.toLowerCase();
    return databases.filter(db => 
      db.name.toLowerCase().includes(lower) ||
      db.url.toLowerCase().includes(lower)
    );
  }, [databases, searchText]);

  const handleSelectDatabase = (database: Database) => {
    navigate(`/databases/${database.name}`);
  };

  const handleOpenModal = () => {
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  const handleAddSuccess = () => {
    setIsModalOpen(false);
    refetch();
  };

  const handleDelete = async (name: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm(`确定要删除数据库连接 "${name}" 吗？`)) {
      setDeleting(name);
      try {
        await apiFetch(`/dbs/${name}`, { method: 'DELETE' });
        message.success(`数据库连接 "${name}" 删除成功`);
        await refetch();
        // If current page is the deleted database, navigate to home
        if (location.pathname === `/databases/${name}`) {
          navigate('/');
        }
      } catch (error: unknown) {
        const err = error as { status?: number; message?: string; error?: string };
        if (err.status === 404) {
          message.warning(`数据库连接 "${name}" 不存在或已被删除`);
          await refetch();
          if (location.pathname === `/databases/${name}`) {
            navigate('/');
          }
        } else {
          message.error(err.message || err.error || `删除数据库连接 "${name}" 失败`);
        }
      } finally {
        setDeleting(null);
      }
    }
  };

  const isDatabaseSelected = (dbName: string) => {
    return location.pathname === `/databases/${dbName}`;
  };

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center gap-2 mb-4">
          <DatabaseOutlined className="text-xl text-gray-700" />
          <Text strong className="text-base text-gray-800">
            DB QUERY TOOL
          </Text>
        </div>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={handleOpenModal}
          block
          className="shadow-sm rounded-lg h-9 font-semibold"
        >
          ADD DATABASE
        </Button>
      </div>

      {/* Search Box */}
      <div className="px-4 py-3 border-b border-gray-100">
        <Input
          placeholder="Search tables, columns..."
          prefix={<SearchOutlined className="text-gray-400" />}
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          allowClear
          className="rounded-lg"
          size="small"
        />
      </div>

      {/* Database List */}
      <div className="flex-1 overflow-auto">
        {isLoading ? (
          <div className="p-4">
            <Skeleton active paragraph={{ rows: 3 }} />
          </div>
        ) : !filteredDatabases || filteredDatabases.length === 0 ? (
          <div className="p-6 text-center">
            <Empty
              description={
                <Text className="text-gray-500 text-sm">
                  {searchText ? '未找到匹配的数据库' : '暂无数据库连接'}
                </Text>
              }
              image={Empty.PRESENTED_IMAGE_SIMPLE}
            />
          </div>
        ) : (
          <div className="p-2 space-y-1">
            {filteredDatabases.map((db) => (
              <div
                key={db.name}
                className={`group cursor-pointer transition-all duration-200 rounded-lg p-2.5 border ${
                  isDatabaseSelected(db.name)
                    ? 'bg-yellow-50 border-yellow-300'
                    : 'bg-white border-transparent hover:bg-gray-50'
                }`}
                onClick={() => handleSelectDatabase(db)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2.5 flex-1 min-w-0">
                    <div className="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center flex-shrink-0">
                      <DatabaseOutlined className="text-white text-sm" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <Text strong className="text-sm text-gray-800 block truncate">
                        {db.name.toUpperCase()}
                      </Text>
                      <Text className="text-xs text-gray-400 block truncate">
                        {db.url.split('/').pop()?.split('?')[0] || 'database'}
                      </Text>
                    </div>
                  </div>
                  <Button
                    type="text"
                    danger
                    size="small"
                    icon={<DeleteOutlined />}
                    onClick={(e) => handleDelete(db.name, e)}
                    loading={deleting === db.name}
                    className="opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0"
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Add Database Modal */}
      <Modal
        title={
          <div className="flex items-center gap-2">
            <PlusOutlined className="text-blue-500" />
            <span className="text-lg font-semibold">新增数据库连接</span>
          </div>
        }
        open={isModalOpen}
        onCancel={handleCloseModal}
        footer={null}
        width={600}
        className="rounded-lg"
      >
        <AddDatabaseForm onSuccess={handleAddSuccess} />
      </Modal>
    </div>
  );
}
