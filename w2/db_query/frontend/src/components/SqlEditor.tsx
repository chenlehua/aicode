/** SQL Editor component with Monaco Editor. */

import { Editor } from '@monaco-editor/react';
import type { editor } from 'monaco-editor';
import * as monaco from 'monaco-editor';
import { Alert } from 'antd';
import { useRef, useEffect } from 'react';

interface SqlEditorProps {
  value: string;
  onChange: (value: string) => void;
  error?: string;
  readOnly?: boolean;
  height?: string;
  onExecute?: () => void;
}

export function SqlEditor({
  value,
  onChange,
  error,
  readOnly = false,
  height = '300px',
  onExecute,
}: SqlEditorProps) {
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);
  const commandIdRef = useRef<string | null>(null);

  const handleEditorDidMount = (editorInstance: editor.IStandaloneCodeEditor) => {
    editorRef.current = editorInstance;

    // Add keyboard shortcut: Ctrl+Enter (or Cmd+Enter on Mac) to execute
    if (onExecute && !readOnly) {
      const commandId = editorInstance.addCommand(
        monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter,
        () => {
          onExecute();
        }
      );
      commandIdRef.current = commandId;
    }
  };

  useEffect(() => {
    if (editorRef.current && onExecute && !readOnly) {
      const editorInstance = editorRef.current;
      const commandId = editorInstance.addCommand(
        monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter,
        () => {
          onExecute();
        }
      );
      commandIdRef.current = commandId;

      return () => {
        if (commandIdRef.current) {
          // Monaco Editor doesn't provide a direct way to remove commands
          // The command will be cleaned up when the editor is disposed
          commandIdRef.current = null;
        }
      };
    }
    return undefined;
  }, [onExecute, readOnly]);

  return (
    <div>
      <Editor
        height={height}
        defaultLanguage="sql"
        value={value}
        onChange={(val) => onChange(val || '')}
        onMount={handleEditorDidMount}
        options={{
          readOnly,
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
          fontSize: 14,
          lineNumbers: 'on',
          roundedSelection: false,
          cursorStyle: 'line',
          automaticLayout: true,
          formatOnPaste: true,
          formatOnType: true,
          wordWrap: 'on',
        }}
        theme="vs-dark"
      />
      {error && (
        <Alert
          message="SQL Error"
          description={error}
          type="error"
          showIcon
          style={{ marginTop: 8 }}
        />
      )}
    </div>
  );
}
