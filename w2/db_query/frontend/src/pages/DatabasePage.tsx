/** Database page showing selected database metadata. */

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button, Spin, Alert, Card, Tabs, message } from 'antd';
import {
  ArrowLeftOutlined,
  PlayCircleOutlined,
  ClearOutlined,
  ThunderboltOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import { useDatabase } from '../hooks/useDatabases';
import { useQuery } from '../hooks/useQuery';
import { useNaturalQuery } from '../hooks/useNaturalQuery';
import { SchemaViewer } from '../components/SchemaViewer';
import { SqlEditor } from '../components/SqlEditor';
import { ResultsTable } from '../components/ResultsTable';
import { QueryHistory } from '../components/QueryHistory';
import { NaturalLanguageInput } from '../components/NaturalLanguageInput';
import { GeneratedSqlPreview } from '../components/GeneratedSqlPreview';
import { apiFetch } from '../services/api';
import type { QueryHistoryList } from '../types';

export function DatabasePage() {
  const { name } = useParams<{ name: string }>();
  const navigate = useNavigate();
  const { data: database, isLoading, isError } = useDatabase(name || '');
  const [sql, setSql] = useState('SELECT * FROM ');
  const [naturalPrompt, setNaturalPrompt] = useState('');
  const [activeTab, setActiveTab] = useState('query');
  const [history, setHistory] = useState<QueryHistoryList | null>(null);
  const [historyLoading, setHistoryLoading] = useState(false);

  const {
    executeQuery,
    loading: queryLoading,
    result,
    error,
  } = useQuery(name || '', {
    onSuccess: () => {
      // Refresh history after successful query
      loadHistory();
    },
  });

  const {
    generateSQL,
    loading: nlLoading,
    result: generatedSQL,
    error: nlError,
  } = useNaturalQuery(name || '', {
    onSuccess: (result) => {
      // Auto-switch to SQL editor tab when SQL is generated
      setActiveTab('query');
      // Optionally auto-fill the SQL editor
      setSql(result.sql);
      message.success('SQL generated successfully');
    },
    onError: (err) => {
      message.error(err.message || 'Failed to generate SQL');
    },
  });

  const loadHistory = async () => {
    if (!name) return;
    setHistoryLoading(true);
    try {
      const data = await apiFetch<QueryHistoryList>(`/dbs/${name}/history?page=1&pageSize=10`);
      setHistory(data);
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setHistoryLoading(false);
    }
  };

  useEffect(() => {
    if (name) {
      loadHistory();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [name]);

  const handleExecute = () => {
    if (sql.trim()) {
      executeQuery(sql);
    }
  };

  const handleReplay = (replaySql: string) => {
    setSql(replaySql);
    setActiveTab('query');
    executeQuery(replaySql);
  };

  const handleGenerateSQL = () => {
    if (naturalPrompt.trim()) {
      generateSQL(naturalPrompt);
    }
  };

  const handleUseGeneratedSQL = (generatedSql: string) => {
    setSql(generatedSql);
    setActiveTab('query');
    message.info('SQL loaded into editor');
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

  const tabItems = [
    {
      key: 'query',
      label: 'SQL Editor',
      children: (
        <div className="space-y-4">
          <Card
            title="SQL Editor"
            extra={
              <div className="flex gap-2">
                <Button icon={<ClearOutlined />} onClick={() => setSql('')} disabled={queryLoading}>
                  Clear
                </Button>
                <Button
                  type="primary"
                  icon={<PlayCircleOutlined />}
                  onClick={handleExecute}
                  loading={queryLoading}
                  disabled={!sql.trim()}
                >
                  Execute
                </Button>
              </div>
            }
          >
            <SqlEditor
              value={sql}
              onChange={setSql}
              error={error || undefined}
              height="200px"
              onExecute={handleExecute}
            />
          </Card>
          <Card title="Results">
            <ResultsTable result={result} loading={queryLoading} />
          </Card>
        </div>
      ),
    },
    {
      key: 'natural',
      label: 'Natural Language',
      children: (
        <div className="space-y-4">
          <Card
            title="Natural Language Query"
            extra={
              <Button
                type="primary"
                icon={<ThunderboltOutlined />}
                onClick={handleGenerateSQL}
                loading={nlLoading}
                disabled={!naturalPrompt.trim()}
              >
                Generate SQL
              </Button>
            }
          >
            <NaturalLanguageInput
              value={naturalPrompt}
              onChange={setNaturalPrompt}
              disabled={nlLoading}
            />
            {nlError && (
              <Alert
                message="Generation Error"
                description={nlError}
                type="error"
                showIcon
                className="mt-4"
              />
            )}
          </Card>
          <GeneratedSqlPreview
            generated={generatedSQL}
            onUseSql={handleUseGeneratedSQL}
            loading={nlLoading}
          />
        </div>
      ),
    },
    {
      key: 'schema',
      label: 'Schema',
      children: <SchemaViewer metadata={database.metadata} />,
    },
    {
      key: 'history',
      label: 'History',
      children: (
        <QueryHistory
          items={history?.items || []}
          onReplay={handleReplay}
          loading={historyLoading}
        />
      ),
    },
  ];

  return (
    <div className="p-6">
      <div className="mb-4 flex justify-between items-center">
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/')} type="text">
          Back to Databases
        </Button>
        {database && (
          <Button icon={<ReloadOutlined />} onClick={handleRefreshMetadata} loading={isLoading}>
            Refresh Metadata
          </Button>
        )}
      </div>
      <Tabs
        items={tabItems}
        activeKey={activeTab}
        onChange={setActiveTab}
        defaultActiveKey="query"
      />
    </div>
  );
}
