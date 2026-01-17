/** Schema browser component with search functionality. */

import { useMemo, useState } from 'react';
import { Collapse, Tag, Empty, Tooltip } from 'antd';
import { TableOutlined, EyeOutlined, KeyOutlined, LinkOutlined, InfoCircleOutlined } from '@ant-design/icons';
import type { DatabaseMetadata, ColumnMetadata } from '../types';

interface SchemaBrowserProps {
  metadata: DatabaseMetadata;
  onTableClick?: (tableName: string) => void;
  searchText?: string;
}

export function SchemaBrowser({ metadata, onTableClick, searchText = '' }: SchemaBrowserProps) {
  // Track expanded keys - default to empty (collapsed) for better performance
  const [expandedTableKeys, setExpandedTableKeys] = useState<string[]>([]);
  const [expandedViewKeys, setExpandedViewKeys] = useState<string[]>([]);

  const filteredTables = useMemo(() => {
    if (!searchText.trim()) {
      return metadata.tables;
    }
    const lowerSearch = searchText.toLowerCase();
    return metadata.tables.filter(
      (table) =>
        table.tableName.toLowerCase().includes(lowerSearch) ||
        table.columns.some((col) => col.name.toLowerCase().includes(lowerSearch))
    );
  }, [metadata.tables, searchText]);

  const filteredViews = useMemo(() => {
    if (!searchText.trim()) {
      return metadata.views;
    }
    const lowerSearch = searchText.toLowerCase();
    return metadata.views.filter(
      (view) =>
        view.tableName.toLowerCase().includes(lowerSearch) ||
        view.columns.some((col) => col.name.toLowerCase().includes(lowerSearch))
    );
  }, [metadata.views, searchText]);

  // When searching, auto-expand matching tables/views
  useMemo(() => {
    if (searchText.trim()) {
      setExpandedTableKeys(filteredTables.map((t) => `table-${t.tableName}`));
      setExpandedViewKeys(filteredViews.map((v) => `view-${v.tableName}`));
    }
  }, [searchText, filteredTables, filteredViews]);

  const renderColumn = (col: ColumnMetadata, tableName: string) => {
    // Build tooltip content for additional info
    const tooltipContent = [];
    if (col.defaultValue) {
      tooltipContent.push(`默认值: ${col.defaultValue}`);
    }
    if (col.references) {
      tooltipContent.push(`引用: ${col.references}`);
    }

    return (
      <div
        key={`${tableName}-${col.name}`}
        className="py-2.5 px-3 border-b border-border-light last:border-0 hover:bg-bg-secondary transition-colors duration-150"
      >
        {/* Row 1: Column Name */}
        <div className="flex items-start gap-2 mb-1.5">
          <span className="font-mono text-sm text-text-primary break-all leading-tight flex-1">
            {col.name}
          </span>
          {tooltipContent.length > 0 && (
            <Tooltip title={tooltipContent.join('\n')} placement="left">
              <InfoCircleOutlined className="text-text-tertiary text-xs flex-shrink-0 mt-0.5 cursor-help" />
            </Tooltip>
          )}
        </div>

        {/* Row 2: Type and Tags */}
        <div className="flex items-center flex-wrap gap-1">
          <Tag className="m-0 bg-bg-tertiary text-text-secondary border-0 text-xs font-mono">
            {col.dataType.toUpperCase()}
          </Tag>
          {col.isPrimaryKey && (
            <Tag color="gold" className="m-0 text-xs">
              <KeyOutlined className="mr-0.5" />
              主键
            </Tag>
          )}
          {col.isForeignKey && (
            <Tooltip title={col.references ? `引用 ${col.references}` : '外键'}>
              <Tag color="cyan" className="m-0 text-xs cursor-help">
                <LinkOutlined className="mr-0.5" />
                外键
              </Tag>
            </Tooltip>
          )}
          {!col.isNullable && (
            <Tag color="orange" className="m-0 text-xs">非空</Tag>
          )}
          {col.defaultValue && (
            <Tooltip title={`默认值: ${col.defaultValue}`}>
              <Tag className="m-0 text-xs bg-accent-green/10 text-accent-green border-0 cursor-help">
                默认
              </Tag>
            </Tooltip>
          )}
        </div>
      </div>
    );
  };

  const tableItems = filteredTables.map((table) => ({
    key: `table-${table.tableName}`,
    label: (
      <div
        className="flex items-center gap-2 cursor-pointer group py-0.5"
        onClick={(e) => {
          e.stopPropagation();
          onTableClick?.(table.tableName);
        }}
      >
        <TableOutlined className="text-accent-blue text-sm flex-shrink-0" />
        <Tooltip title={table.tableName} placement="top">
          <span className="font-mono text-sm font-medium text-text-primary group-hover:text-accent-blue transition-colors truncate max-w-[140px]">
            {table.tableName}
          </span>
        </Tooltip>
        <span className="text-xs text-text-tertiary flex-shrink-0 ml-auto tabular-nums">
          {table.columns.length} 列
        </span>
      </div>
    ),
    children: (
      <div className="bg-white border border-border-light rounded-lg overflow-hidden mt-1 shadow-xs max-h-80 overflow-y-auto">
        {table.columns.map((col) => renderColumn(col, table.tableName))}
      </div>
    ),
  }));

  const viewItems = filteredViews.map((view) => ({
    key: `view-${view.tableName}`,
    label: (
      <div className="flex items-center gap-2 py-0.5">
        <EyeOutlined className="text-accent-green text-sm flex-shrink-0" />
        <Tooltip title={view.tableName} placement="top">
          <span className="font-mono text-sm font-medium text-text-primary truncate max-w-[140px]">
            {view.tableName}
          </span>
        </Tooltip>
        <span className="text-xs text-text-tertiary flex-shrink-0 ml-auto tabular-nums">
          {view.columns.length} 列
        </span>
      </div>
    ),
    children: (
      <div className="bg-white border border-border-light rounded-lg overflow-hidden mt-1 shadow-xs max-h-80 overflow-y-auto">
        {view.columns.map((col) => renderColumn(col, view.tableName))}
      </div>
    ),
  }));

  // Toggle all tables/views
  const toggleAllTables = () => {
    const allKeys = filteredTables.map((t) => `table-${t.tableName}`);
    if (expandedTableKeys.length === allKeys.length) {
      setExpandedTableKeys([]);
    } else {
      setExpandedTableKeys(allKeys);
    }
  };

  const toggleAllViews = () => {
    const allKeys = filteredViews.map((v) => `view-${v.tableName}`);
    if (expandedViewKeys.length === allKeys.length) {
      setExpandedViewKeys([]);
    } else {
      setExpandedViewKeys(allKeys);
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="flex-1 overflow-auto">
        {filteredTables.length === 0 && filteredViews.length === 0 ? (
          <Empty
            description={
              <span className="text-text-tertiary text-sm">
                {searchText ? '未找到匹配的表或视图' : '暂无表或视图'}
              </span>
            }
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            className="py-12"
          />
        ) : (
          <div className="space-y-6">
            {filteredTables.length > 0 && (
              <div>
                <div className="mb-3 pb-2 border-b border-border-light flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <TableOutlined className="text-accent-blue text-xs" />
                    <span className="text-xs font-semibold text-text-secondary uppercase tracking-wide">
                      表
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={toggleAllTables}
                      className="text-xs text-text-tertiary hover:text-accent-blue transition-colors"
                    >
                      {expandedTableKeys.length === filteredTables.length ? '全部折叠' : '全部展开'}
                    </button>
                    <span className="text-xs font-medium text-accent-primary bg-accent-primary/10 px-2 py-0.5 rounded-full">
                      {filteredTables.length}
                    </span>
                  </div>
                </div>
                <Collapse
                  items={tableItems}
                  activeKey={expandedTableKeys}
                  onChange={(keys) => setExpandedTableKeys(keys as string[])}
                  size="small"
                  ghost
                  className="schema-collapse"
                />
              </div>
            )}
            {filteredViews.length > 0 && (
              <div>
                <div className="mb-3 pb-2 border-b border-border-light flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <EyeOutlined className="text-accent-green text-xs" />
                    <span className="text-xs font-semibold text-text-secondary uppercase tracking-wide">
                      视图
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={toggleAllViews}
                      className="text-xs text-text-tertiary hover:text-accent-green transition-colors"
                    >
                      {expandedViewKeys.length === filteredViews.length ? '全部折叠' : '全部展开'}
                    </button>
                    <span className="text-xs font-medium text-accent-green bg-accent-green/10 px-2 py-0.5 rounded-full">
                      {filteredViews.length}
                    </span>
                  </div>
                </div>
                <Collapse
                  items={viewItems}
                  activeKey={expandedViewKeys}
                  onChange={(keys) => setExpandedViewKeys(keys as string[])}
                  size="small"
                  ghost
                  className="schema-collapse"
                />
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
