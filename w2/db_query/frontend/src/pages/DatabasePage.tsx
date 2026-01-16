/** Database page showing selected database metadata. */

import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { Button, Spin, Alert, Tabs, message, Typography, Input } from 'antd';
import {
  SearchOutlined,
  PlayCircleOutlined,
  ReloadOutlined,
  DatabaseOutlined,
} from '@ant-design/icons';
import { useDatabase } from '../hooks/useDatabases';
import { useQuery } from '../hooks/useQuery';
import { useNaturalQuery } from '../hooks/useNaturalQuery';
import { SchemaBrowser } from '../components/SchemaBrowser';
import { SqlEditor } from '../components/SqlEditor';
import { ResultsTable } from '../components/ResultsTable';
import { NaturalLanguageInput } from '../components/NaturalLanguageInput';
import { apiFetch } from '../services/api';

const { Text } = Typography;

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
      message.success('SQL generated successfully');
    },
    onError: (err) => {
      message.error(err.message || 'Failed to generate SQL');
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
      message.loading({ content: 'Refreshing metadata...', key: 'refresh' });
      // Re-fetch database metadata by updating the connection
      await apiFetch(`/dbs/${name}`, {
        method: 'PUT',
        body: JSON.stringify({ url: database.url }),
      });
      message.success({ content: 'Metadata refreshed successfully', key: 'refresh' });
      // Reload page to show updated metadata
      window.location.reload();
    } catch (err) {
      message.error({
        content: 'Failed to refresh metadata',
        key: 'refresh',
      });
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Spin size="large" />
      </div>
    );
  }

  if (isError || !database) {
    return (
      <div className="p-6">
        <Alert
          message="Error"
          description={isError ? 'Failed to load database information' : 'Database not found'}
          type="error"
          showIcon
        />
      </div>
    );
  }

  const resultRowCount = result?.rowCount || 0;

  return (
    <div className="h-screen flex flex-col bg-gray-50 overflow-hidden">
      {/* Top Bar - Split between Schema Header and Stats */}
      <div className="bg-white border-b border-gray-200 flex items-stretch">
        {/* Left: Schema Header (aligned with schema browser width) */}
        <div className="w-72 border-r border-gray-200 p-3 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-2">
            <DatabaseOutlined className="text-gray-600" />
            <Text strong className="text-sm text-gray-800 uppercase">
              {database.name}
            </Text>
          </div>
          <Button
            size="small"
            icon={<ReloadOutlined />}
            onClick={handleRefreshMetadata}
            loading={isLoading}
            className="font-semibold text-xs"
          >
            REFRESH
          </Button>
        </div>

        {/* Right: Statistics */}
        <div className="flex-1 flex items-center">
          <div className="flex-1 flex items-center justify-center border-r border-gray-200 py-3">
            <div className="text-center">
              <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider">TABLES</div>
              <div className="text-2xl font-bold text-gray-800">
                {database.metadata.tableCount}
              </div>
            </div>
          </div>
          <div className="flex-1 flex items-center justify-center border-r border-gray-200 py-3">
            <div className="text-center">
              <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider">VIEWS</div>
              <div className="text-2xl font-bold text-gray-800">
                {database.metadata.viewCount}
              </div>
            </div>
          </div>
          <div className="flex-1 flex items-center justify-center border-r border-gray-200 py-3">
            <div className="text-center">
              <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider">ROWS</div>
              <div className={`text-2xl font-bold ${resultRowCount > 0 ? 'text-green-600' : 'text-gray-800'}`}>
                {resultRowCount}
              </div>
            </div>
          </div>
          <div className="flex-1 flex items-center justify-center py-3">
            <div className="text-center">
              <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider">TIME</div>
              <div className={`text-2xl font-bold ${result ? 'text-amber-500' : 'text-gray-800'}`}>
                {result ? `${result.executionTimeMs}ms` : '-'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left: Schema Browser */}
        <div className="w-72 bg-white border-r border-gray-200 flex flex-col overflow-hidden">
          {/* Search */}
          <div className="p-3 border-b border-gray-100">
            <Input
              placeholder="Search tables, columns..."
              prefix={<SearchOutlined className="text-gray-400" />}
              value={schemaSearch}
              onChange={(e) => setSchemaSearch(e.target.value)}
              allowClear
              size="small"
              className="rounded"
            />
          </div>
          {/* Schema Content */}
          <div className="flex-1 overflow-auto p-3">
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
          <div className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
            <Text strong className="text-sm text-gray-700 uppercase tracking-wide">
              QUERY EDITOR
            </Text>
            <Button
              type="primary"
              icon={<PlayCircleOutlined />}
              onClick={queryTab === 'manual' ? handleExecute : handleGenerateSQL}
              loading={queryTab === 'manual' ? queryLoading : nlLoading}
              disabled={queryTab === 'manual' ? !sql.trim() : !naturalPrompt.trim()}
              className="font-semibold rounded-lg px-6"
              style={{ backgroundColor: '#d4a700', borderColor: '#d4a700' }}
            >
              {queryTab === 'manual' ? 'EXECUTE' : 'GENERATE SQL'}
            </Button>
          </div>

          {/* Tabs */}
          <div className="bg-white border-b border-gray-200">
            <Tabs
              activeKey={queryTab}
              onChange={(key) => setQueryTab(key as 'manual' | 'natural')}
              className="px-4"
              items={[
                {
                  key: 'manual',
                  label: <span className="font-semibold text-xs uppercase">MANUAL SQL</span>,
                },
                {
                  key: 'natural',
                  label: <span className="font-semibold text-xs uppercase">NATURAL LANGUAGE</span>,
                },
              ]}
            />
          </div>

          {/* Editor Content - Fixed height for both tabs */}
          <div 
            className={`flex-shrink-0 border-b border-gray-200 ${queryTab === 'manual' ? 'bg-gray-900' : 'bg-white p-4'}`}
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
                placeholder="DESCRIBE YOUR QUERY IN NATURAL LANGUAGE (English or Chinese)"
              />
            )}
          </div>

          {/* Natural Language Error */}
          {nlError && queryTab === 'natural' && (
            <div className="bg-white px-4 py-2 border-b border-gray-200">
              <Alert
                message="Generation Failed"
                description={nlError}
                type="error"
                showIcon
                className="rounded-lg"
              />
            </div>
          )}

          {/* SQL Error */}
          {error && queryTab === 'manual' && (
            <div className="bg-white px-4 py-2 border-b border-gray-200">
              <Alert
                message="SQL Error"
                description={error}
                type="error"
                showIcon
                className="rounded-lg"
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
