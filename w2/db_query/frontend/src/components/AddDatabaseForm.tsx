/** Component for adding a new database connection. */

import { useState } from 'react';
import { Form, Input, Button, message } from 'antd';
import { DatabaseOutlined, LinkOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { apiFetch } from '../services/api';

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
    } catch (error: unknown) {
      const err = error as { message?: string; error?: string };
      message.error(err.message || err.error || '添加数据库连接失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="pt-4">
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        autoComplete="off"
        requiredMark={false}
      >
        <Form.Item
          label={
            <span className="flex items-center gap-2 text-sm font-medium text-text-primary">
              <DatabaseOutlined className="text-accent-primary" />
              数据库名称
            </span>
          }
          name="name"
          rules={[
            { required: true, message: '请输入数据库名称' },
            {
              pattern: /^[a-zA-Z0-9_-]{1,64}$/,
              message: '名称必须为1-64个字符，只能包含字母、数字、下划线和连字符',
            },
          ]}
        >
          <Input
            placeholder="例如：production_db"
            className="h-11 rounded-xl"
          />
        </Form.Item>

        <Form.Item
          label={
            <span className="flex items-center gap-2 text-sm font-medium text-text-primary">
              <LinkOutlined className="text-accent-blue" />
              连接 URL
            </span>
          }
          name="url"
          rules={[
            { required: true, message: '请输入连接URL' },
            {
              pattern: /^postgres(ql)?:\/\/.*/,
              message: 'URL必须以 postgres:// 或 postgresql:// 开头',
            },
          ]}
          extra={
            <span className="text-xs text-text-tertiary mt-1 block">
              格式：postgres://用户名:密码@主机:端口/数据库名
            </span>
          }
        >
          <Input
            placeholder="postgres://user:password@host:port/database"
            className="h-11 rounded-xl"
          />
        </Form.Item>

        <Form.Item className="mb-0 mt-6">
          <Button
            type="primary"
            htmlType="submit"
            icon={<CheckCircleOutlined />}
            loading={loading}
            block
            className="h-12 text-base font-semibold"
          >
            添加数据库
          </Button>
        </Form.Item>
      </Form>

      {/* Helper Tips */}
      <div className="mt-6 p-4 bg-bg-secondary rounded-xl">
        <p className="text-xs font-semibold text-text-secondary uppercase tracking-wide mb-2">
          支持的数据库
        </p>
        <div className="flex items-center gap-2">
          <span className="px-2.5 py-1 bg-accent-blue/10 text-accent-blue text-xs font-medium rounded-full">
            PostgreSQL
          </span>
        </div>
      </div>
    </div>
  );
}
