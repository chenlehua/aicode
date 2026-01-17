/** Custom sidebar component with database list and add button. */

import { useState, useMemo } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button, Empty, Skeleton, Modal, message, Input } from 'antd';
import { PlusOutlined, DeleteOutlined, DatabaseOutlined, SearchOutlined } from '@ant-design/icons';
import { useDatabases } from '../hooks/useDatabases';
import { AddDatabaseForm } from './AddDatabaseForm';
import { apiFetch } from '../services/api';
import type { Database } from '../types';

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
    <div className="sidebar">
      {/* Header */}
      <div className="sidebar-header">
        <div className="flex items-center gap-3 mb-5">
          <div className="w-10 h-10 rounded-xl bg-accent-primary flex items-center justify-center shadow-sm">
            <DatabaseOutlined className="text-lg text-text-primary" />
          </div>
          <div>
            <h1 className="text-base font-bold text-text-primary tracking-tight">
              DB Query
            </h1>
            <p className="text-xs text-text-tertiary">自然语言 SQL 工具</p>
          </div>
        </div>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={handleOpenModal}
          block
          className="h-11 text-sm font-semibold"
        >
          添加数据库
        </Button>
      </div>

      {/* Search Box */}
      <div className="px-5 py-4 border-b border-border-light">
        <Input
          placeholder="搜索数据库..."
          prefix={<SearchOutlined className="text-text-tertiary" />}
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          allowClear
          className="rounded-lg"
        />
      </div>

      {/* Database List */}
      <div className="flex-1 overflow-auto p-3">
        {isLoading ? (
          <div className="p-4">
            <Skeleton active paragraph={{ rows: 3 }} />
          </div>
        ) : !filteredDatabases || filteredDatabases.length === 0 ? (
          <div className="py-12 text-center">
            <Empty
              description={
                <span className="text-text-tertiary text-sm">
                  {searchText ? '未找到匹配的数据库' : '暂无数据库连接'}
                </span>
              }
              image={Empty.PRESENTED_IMAGE_SIMPLE}
            />
          </div>
        ) : (
          <div className="space-y-2">
            {filteredDatabases.map((db, index) => (
              <div
                key={db.name}
                className={`sidebar-item group animate-slide-in-left ${
                  isDatabaseSelected(db.name) ? 'active' : ''
                }`}
                style={{ animationDelay: `${index * 50}ms` }}
                onClick={() => handleSelectDatabase(db)}
              >
                <div className="flex items-center justify-between w-full">
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 transition-colors ${
                      isDatabaseSelected(db.name)
                        ? 'bg-accent-primary'
                        : 'bg-accent-green/20 group-hover:bg-accent-green/30'
                    }`}>
                      <DatabaseOutlined className={`text-base ${
                        isDatabaseSelected(db.name) ? 'text-text-primary' : 'text-accent-green'
                      }`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-semibold text-sm text-text-primary truncate">
                        {db.name}
                      </div>
                      <div className="text-xs text-text-tertiary truncate">
                        {db.url.split('/').pop()?.split('?')[0] || 'database'}
                      </div>
                    </div>
                  </div>
                  <Button
                    type="text"
                    danger
                    size="small"
                    icon={<DeleteOutlined />}
                    onClick={(e) => handleDelete(db.name, e)}
                    loading={deleting === db.name}
                    className="opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0 ml-2"
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-5 py-4 border-t border-border-light">
        <p className="text-xs text-text-tertiary text-center">
          {databases?.length || 0} 个数据库连接
        </p>
      </div>

      {/* Add Database Modal */}
      <Modal
        title={
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-accent-primary flex items-center justify-center">
              <PlusOutlined className="text-text-primary" />
            </div>
            <span className="text-lg font-semibold">添加数据库连接</span>
          </div>
        }
        open={isModalOpen}
        onCancel={handleCloseModal}
        footer={null}
        width={520}
      >
        <AddDatabaseForm onSuccess={handleAddSuccess} />
      </Modal>
    </div>
  );
}
