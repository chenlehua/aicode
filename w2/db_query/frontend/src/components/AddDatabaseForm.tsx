/** Component for adding a new database connection. */

import { useState } from 'react';
import { Card, Form, Input, Button, message } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { apiFetch } from '../services/api';

// Toast notifications are already using Ant Design's message API

interface AddDatabaseFormProps {
  onSuccess?: () => void;
}

export function AddDatabaseForm({ onSuccess }: AddDatabaseFormProps) {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (values: { name: string; url: string }) => {
    setLoading(true);
    try {
      await apiFetch(`/dbs/${values.name}`, {
        method: 'PUT',
        body: JSON.stringify({ url: values.url }),
      });
      message.success(`Database "${values.name}" added successfully`);
      form.resetFields();
      onSuccess?.();
      // Reload to refresh database list
      window.location.reload();
    } catch (error: unknown) {
      const err = error as { message?: string; error?: string };
      message.error(err.message || err.error || 'Failed to add database connection');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card title="Add Database Connection">
      <Form form={form} layout="vertical" onFinish={handleSubmit} autoComplete="off">
        <Form.Item
          label="Database Name"
          name="name"
          rules={[
            { required: true, message: 'Please enter a database name' },
            {
              pattern: /^[a-zA-Z0-9_-]{1,64}$/,
              message: 'Name must be 1-64 characters, alphanumeric with underscores/hyphens',
            },
          ]}
        >
          <Input placeholder="e.g., production_db" />
        </Form.Item>

        <Form.Item
          label="Connection URL"
          name="url"
          rules={[
            { required: true, message: 'Please enter a connection URL' },
            {
              pattern: /^postgres(ql)?:\/\/.*/,
              message: 'URL must start with postgres:// or postgresql://',
            },
          ]}
        >
          <Input placeholder="postgres://user:password@host:port/database" type="password" />
        </Form.Item>

        <Form.Item>
          <Button type="primary" htmlType="submit" icon={<PlusOutlined />} loading={loading} block>
            Add Database
          </Button>
        </Form.Item>
      </Form>
    </Card>
  );
}
