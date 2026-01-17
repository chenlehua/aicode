/** Database page showing selected database metadata. */

import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { Button, Spin, Alert, Tabs, message, Input } from 'antd';
import {
  SearchOutlined,
  PlayCircleOutlined,
  ReloadOutlined,
  DatabaseOutlined,
  TableOutlined,
  EyeOutlined,
  ClockCircleOutlined,
  NumberOutlined,
} from '@ant-design/icons';
import { useDatabase } from '../hooks/useDatabases';
import { useQuery } from '../hooks/useQuery';
import { useNaturalQuery } from '../hooks/useNaturalQuery';
import { SchemaBrowser } from '../components/SchemaBrowser';
import { SqlEditor } from '../components/SqlEditor';
import { ResultsTable } from '../components/ResultsTable';
import { NaturalLanguageInput } from '../components/NaturalLanguageInput';
import { apiFetch } from '../services/api';

export function DatabasePage() {
  const { name } = useParams<{ name: string }>();
  const { data: database, isLoading, isError } = useDatabase(name || '');
  const [sql, setSql] = useState('SELECT * FROM ');
  const [naturalPrompt, setNaturalPrompt] = useState('');
  const [queryTab, setQueryTab] = useState<'manual' | 'natural'>('manual');
  const [schemaSearch, setSchemaSearch] = useState('');

  const {
    executeQuery,
    loading: queryLoading,
    result,
    error,
  } = useQuery(name || '');

  const {
    generateSQL,
    loading: nlLoading,
    error: nlError,
  } = useNaturalQuery(name || '', {
    onSuccess: (result) => {
      // Auto-switch to manual SQL tab when SQL is generated
      setQueryTab('manual');
      // Auto-fill the SQL editor
      setSql(result.sql);
      message.success('SQL 生成成功');
    },
    onError: (err) => {
      message.error(err.message || 'SQL 生成失败');
    },
  });

  const handleExecute = () => {
    if (sql.trim()) {
      executeQuery(sql);
    }
  };

  const handleTableClick = (tableName: string) => {
    setSql(`SELECT * FROM ${tableName} LIMIT 100;`);
    setQueryTab('manual');
  };

  const handleGenerateSQL = () => {
    if (naturalPrompt.trim()) {
      generateSQL(naturalPrompt);
    }
  };

  const handleRefreshMetadata = async () => {
    if (!name || !database) return;

    try {
      message.loading({ content: '正在刷新元数据...', key: 'refresh' });
      // Re-fetch database metadata by updating the connection
      await apiFetch(`/dbs/${name}`, {
        method: 'PUT',
        body: JSON.stringify({ url: database.url }),
      });
      message.success({ content: '元数据刷新成功', key: 'refresh' });
      // Reload page to show updated metadata
      window.location.reload();
    } catch (err) {
      message.error({
        content: '元数据刷新失败',
        key: 'refresh',
      });
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen bg-bg-secondary">
        <div className="text-center">
          <Spin size="large" />
          <p className="mt-4 text-text-secondary">加载数据库信息...</p>
        </div>
      </div>
    );
  }

  if (isError || !database) {
    return (
      <div className="p-8 bg-bg-secondary min-h-screen">
        <Alert
          message="加载失败"
          description={isError ? '无法加载数据库信息' : '数据库不存在'}
          type="error"
          showIcon
          className="max-w-lg mx-auto"
        />
      </div>
    );
  }

  const resultRowCount = result?.rowCount || 0;

  return (
    <div className="h-screen flex flex-col bg-bg-secondary overflow-hidden">
      {/* Top Header Bar */}
      <div className="bg-white border-b border-border-light flex items-stretch shadow-xs">
        {/* Left: Database Info (aligned with schema browser width) */}
        <div className="w-72 border-r border-border-light p-4 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-accent-primary flex items-center justify-center">
              <DatabaseOutlined className="text-text-primary" />
            </div>
            <div>
              <h2 className="font-bold text-sm text-text-primary">
                {database.name}
              </h2>
              <p className="text-xs text-text-tertiary">PostgreSQL</p>
            </div>
          </div>
          <Button
            size="small"
            icon={<ReloadOutlined />}
            onClick={handleRefreshMetadata}
            loading={isLoading}
            className="font-medium text-xs"
          >
            刷新
          </Button>
        </div>

        {/* Right: Statistics Cards */}
        <div className="flex-1 flex items-stretch">
          <div className="stat-card flex-1">
            <div className="flex items-center gap-1.5 mb-1">
              <TableOutlined className="text-text-tertiary text-xs" />
              <span className="stat-label">表</span>
            </div>
            <span className="stat-value">{database.metadata.tableCount}</span>
          </div>
          <div className="stat-card flex-1">
            <div className="flex items-center gap-1.5 mb-1">
              <EyeOutlined className="text-text-tertiary text-xs" />
              <span className="stat-label">视图</span>
            </div>
            <span className="stat-value">{database.metadata.viewCount}</span>
          </div>
          <div className="stat-card flex-1">
            <div className="flex items-center gap-1.5 mb-1">
              <NumberOutlined className="text-text-tertiary text-xs" />
              <span className="stat-label">结果行数</span>
            </div>
            <span className={`stat-value ${resultRowCount > 0 ? 'text-accent-green' : ''}`}>
              {resultRowCount}
            </span>
          </div>
          <div className="stat-card flex-1 border-r-0">
            <div className="flex items-center gap-1.5 mb-1">
              <ClockCircleOutlined className="text-text-tertiary text-xs" />
              <span className="stat-label">执行时间</span>
            </div>
            <span className={`stat-value ${result ? 'text-accent-secondary' : ''}`}>
              {result ? `${result.executionTimeMs}ms` : '-'}
            </span>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left: Schema Browser */}
        <div className="w-72 bg-white border-r border-border-light flex flex-col overflow-hidden">
          {/* Search */}
          <div className="p-4 border-b border-border-light">
            <Input
              placeholder="搜索表、列..."
              prefix={<SearchOutlined className="text-text-tertiary" />}
              value={schemaSearch}
              onChange={(e) => setSchemaSearch(e.target.value)}
              allowClear
              className="rounded-lg"
            />
          </div>
          {/* Schema Content */}
          <div className="flex-1 overflow-auto p-4">
            <SchemaBrowser
              metadata={database.metadata}
              onTableClick={handleTableClick}
              searchText={schemaSearch}
            />
          </div>
        </div>

        {/* Right: Query Editor & Results */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Query Editor Header */}
          <div className="page-header">
            <div className="flex items-center gap-3">
              <span className="text-sm font-semibold text-text-primary uppercase tracking-wide">
                查询编辑器
              </span>
              <span className="text-xs px-2.5 py-1 bg-bg-tertiary rounded-full text-text-secondary">
                {queryTab === 'manual' ? 'SQL' : '自然语言'}
              </span>
            </div>
            <Button
              type="primary"
              icon={<PlayCircleOutlined />}
              onClick={queryTab === 'manual' ? handleExecute : handleGenerateSQL}
              loading={queryTab === 'manual' ? queryLoading : nlLoading}
              disabled={queryTab === 'manual' ? !sql.trim() : !naturalPrompt.trim()}
              className="h-10 px-6 font-semibold"
            >
              {queryTab === 'manual' ? '执行查询' : '生成 SQL'}
            </Button>
          </div>

          {/* Tabs */}
          <div className="bg-white border-b border-border-light px-6">
            <Tabs
              activeKey={queryTab}
              onChange={(key) => setQueryTab(key as 'manual' | 'natural')}
              items={[
                {
                  key: 'manual',
                  label: <span className="font-semibold text-xs uppercase tracking-wide">SQL 编辑</span>,
                },
                {
                  key: 'natural',
                  label: <span className="font-semibold text-xs uppercase tracking-wide">自然语言</span>,
                },
              ]}
            />
          </div>

          {/* Editor Content - Fixed height for both tabs */}
          <div
            className={`flex-shrink-0 border-b border-border-light ${queryTab === 'manual' ? 'bg-gray-900' : 'bg-white p-6'}`}
            style={{ height: '200px' }}
          >
            {queryTab === 'manual' ? (
              <SqlEditor
                value={sql}
                onChange={setSql}
                error={error || undefined}
                height="200px"
                onExecute={handleExecute}
              />
            ) : (
              <NaturalLanguageInput
                value={naturalPrompt}
                onChange={setNaturalPrompt}
                disabled={nlLoading}
                placeholder="用自然语言描述您的查询需求（支持中文和英文）"
              />
            )}
          </div>

          {/* Natural Language Error */}
          {nlError && queryTab === 'natural' && (
            <div className="bg-white px-6 py-3 border-b border-border-light">
              <Alert
                message="生成失败"
                description={nlError}
                type="error"
                showIcon
              />
            </div>
          )}

          {/* SQL Error */}
          {error && queryTab === 'manual' && (
            <div className="bg-white px-6 py-3 border-b border-border-light">
              <Alert
                message="SQL 错误"
                description={error}
                type="error"
                showIcon
              />
            </div>
          )}

          {/* Results Area */}
          <div className="flex-1 overflow-auto bg-white">
            <ResultsTable result={result} loading={queryLoading} />
          </div>
        </div>
      </div>
    </div>
  );
}
