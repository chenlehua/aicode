/** Home page with database list and add form. */

import { Row, Col } from 'antd';
import { useNavigate } from 'react-router-dom';
import { DatabaseList } from '../components/DatabaseList';
import { AddDatabaseForm } from '../components/AddDatabaseForm';
import type { Database } from '../types';

export function HomePage() {
  const navigate = useNavigate();

  const handleSelectDatabase = (database: Database) => {
    navigate(`/databases/${database.name}`);
  };

  return (
    <div className="p-6">
      <Row gutter={[24, 24]}>
        <Col xs={24} lg={8}>
          <AddDatabaseForm />
        </Col>
        <Col xs={24} lg={16}>
          <DatabaseList onSelect={handleSelectDatabase} />
        </Col>
      </Row>
    </div>
  );
}
