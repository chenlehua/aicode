/** Component for adding a new database connection. */

import { useState } from 'react';
import { Form, Input, Button, message } from 'antd';
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
      message.success(`数据库 "${values.name}" 添加成功`);
      form.resetFields();
      onSuccess?.();
      // Reload to refresh database list
      window.location.reload();
    } catch (error: unknown) {
      const err = error as { message?: string; error?: string };
      message.error(err.message || err.error || '添加数据库连接失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Form form={form} layout="vertical" onFinish={handleSubmit} autoComplete="off">
      <Form.Item
        label="数据库名称"
        name="name"
        rules={[
          { required: true, message: '请输入数据库名称' },
          {
            pattern: /^[a-zA-Z0-9_-]{1,64}$/,
            message: '名称必须为1-64个字符，只能包含字母、数字、下划线和连字符',
          },
        ]}
      >
        <Input placeholder="例如：production_db" />
      </Form.Item>

      <Form.Item
        label="连接URL"
        name="url"
        rules={[
          { required: true, message: '请输入连接URL' },
          {
            pattern: /^postgres(ql)?:\/\/.*/,
            message: 'URL必须以 postgres:// 或 postgresql:// 开头',
          },
        ]}
      >
        <Input placeholder="postgres://user:password@host:port/database" />
      </Form.Item>

      <Form.Item>
        <Button type="primary" htmlType="submit" icon={<PlusOutlined />} loading={loading} block>
          添加数据库
        </Button>
      </Form.Item>
    </Form>
  );
}
