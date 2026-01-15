/** Home page with database list and add form. */

import { useState } from 'react';
import { Button, Modal } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { DatabaseList } from '../components/DatabaseList';
import { AddDatabaseForm } from '../components/AddDatabaseForm';
import type { Database } from '../types';

export function HomePage() {
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);

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
  };

  return (
    <div className="p-6">
      <div className="mb-4 flex justify-end">
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={handleOpenModal}
          size="large"
        >
          新增数据库连接
        </Button>
      </div>
      <DatabaseList onSelect={handleSelectDatabase} />
      <Modal
        title="新增数据库连接"
        open={isModalOpen}
        onCancel={handleCloseModal}
        footer={null}
        width={600}
      >
        <AddDatabaseForm onSuccess={handleAddSuccess} />
      </Modal>
    </div>
  );
}
