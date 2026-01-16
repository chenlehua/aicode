/** Component showing generated SQL with explanation. */

import { Card, Alert, Button } from 'antd';
import { CopyOutlined, CheckOutlined } from '@ant-design/icons';
import { useState } from 'react';
import { Editor } from '@monaco-editor/react';
import type { GeneratedSQL } from '../types';

interface GeneratedSqlPreviewProps {
  generated: GeneratedSQL | null;
  onUseSql?: (sql: string) => void;
  loading?: boolean;
}

export function GeneratedSqlPreview({
  generated,
  onUseSql,
  loading = false,
}: GeneratedSqlPreviewProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (generated?.sql) {
      await navigator.clipboard.writeText(generated.sql);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (loading) {
    return (
      <Card>
        <div className="text-center text-gray-500">Generating SQL...</div>
      </Card>
    );
  }

  if (!generated) {
    return (
      <Card>
        <Alert
          message="No SQL Generated"
          description="Enter a natural language prompt and click Generate to see SQL here"
          type="info"
          showIcon
        />
      </Card>
    );
  }

  return (
    <Card
      title="Generated SQL"
      extra={
        <div className="flex gap-2">
          <Button
            icon={copied ? <CheckOutlined /> : <CopyOutlined />}
            onClick={handleCopy}
            size="small"
          >
            {copied ? 'Copied!' : 'Copy'}
          </Button>
          {onUseSql && (
            <Button type="primary" onClick={() => onUseSql(generated.sql)} size="small">
              Use in Editor
            </Button>
          )}
        </div>
      }
    >
      {generated.explanation && (
        <Alert message={generated.explanation} type="info" showIcon className="mb-4" />
      )}
      <Editor
        height="200px"
        defaultLanguage="sql"
        value={generated.sql}
        options={{
          readOnly: true,
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
          fontSize: 14,
          lineNumbers: 'on',
          automaticLayout: true,
          wordWrap: 'on',
        }}
        theme="vs"
      />
    </Card>
  );
}
