/** Component for adding or editing a database connection. */

import { useState, useEffect } from 'react';
import { Form, Input, Button, message } from 'antd';
import { DatabaseOutlined, LinkOutlined, CheckCircleOutlined, FileTextOutlined } from '@ant-design/icons';
import { apiFetch } from '../services/api';
import type { Database } from '../types';

const { TextArea } = Input;

interface DatabaseFormProps {
  /** Existing database data for edit mode */
  database?: Database;
  /** Whether the form is in view-only mode */
  viewOnly?: boolean;
  /** Callback on successful save */
  onSuccess?: () => void;
  /** Callback to cancel/close */
  onCancel?: () => void;
}

export function AddDatabaseForm({ database, viewOnly = false, onSuccess, onCancel }: DatabaseFormProps) {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const isEditMode = !!database;

  // Populate form when editing
  useEffect(() => {
    if (database) {
      form.setFieldsValue({
        name: database.name,
        url: database.url,
        description: database.description || '',
      });
    } else {
      form.resetFields();
    }
  }, [database, form]);

  const handleSubmit = async (values: { name: string; url: string; description?: string }) => {
    setLoading(true);
    try {
      await apiFetch(`/dbs/${values.name}`, {
        method: 'PUT',
        body: JSON.stringify({
          url: values.url,
          description: values.description || '',
        }),
      });
      message.success(isEditMode ? `数据库 "${values.name}" 更新成功` : `数据库 "${values.name}" 添加成功`);
      form.resetFields();
      onSuccess?.();
    } catch (error: unknown) {
      const err = error as { message?: string; error?: string };
      message.error(err.message || err.error || (isEditMode ? '更新数据库连接失败' : '添加数据库连接失败'));
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
        disabled={viewOnly}
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
            disabled={isEditMode} // Name cannot be changed in edit mode
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
            !viewOnly && (
              <span className="text-xs text-text-tertiary mt-1 block">
                格式：postgres://用户名:密码@主机:端口/数据库名
              </span>
            )
          }
        >
          <Input
            placeholder="postgres://user:password@host:port/database"
            className="h-11 rounded-xl"
          />
        </Form.Item>

        <Form.Item
          label={
            <span className="flex items-center gap-2 text-sm font-medium text-text-primary">
              <FileTextOutlined className="text-accent-green" />
              描述
              <span className="text-text-tertiary font-normal">（可选）</span>
            </span>
          }
          name="description"
        >
          <TextArea
            placeholder="添加数据库描述，例如：生产环境主数据库"
            className="rounded-xl"
            rows={3}
            maxLength={500}
            showCount
          />
        </Form.Item>

        {!viewOnly && (
          <Form.Item className="mb-0 mt-6">
            <div className="flex gap-3">
              {onCancel && (
                <Button
                  onClick={onCancel}
                  className="flex-1 h-12 text-base font-medium"
                >
                  取消
                </Button>
              )}
              <Button
                type="primary"
                htmlType="submit"
                icon={<CheckCircleOutlined />}
                loading={loading}
                className={`h-12 text-base font-semibold ${onCancel ? 'flex-1' : 'w-full'}`}
              >
                {isEditMode ? '保存修改' : '添加数据库'}
              </Button>
            </div>
          </Form.Item>
        )}

        {viewOnly && onCancel && (
          <Form.Item className="mb-0 mt-6">
            <Button onClick={onCancel} block className="h-12 text-base font-medium">
              关闭
            </Button>
          </Form.Item>
        )}
      </Form>

      {/* Helper Tips */}
      {!viewOnly && !isEditMode && (
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
      )}
    </div>
  );
}
