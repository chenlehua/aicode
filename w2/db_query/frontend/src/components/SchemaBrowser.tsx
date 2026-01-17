/** Schema browser component with search functionality. */

import { useMemo } from 'react';
import { Collapse, Tag, Empty } from 'antd';
import { TableOutlined, EyeOutlined, KeyOutlined, LinkOutlined } from '@ant-design/icons';
import type { DatabaseMetadata, ColumnMetadata } from '../types';

interface SchemaBrowserProps {
  metadata: DatabaseMetadata;
  onTableClick?: (tableName: string) => void;
  searchText?: string;
}

export function SchemaBrowser({ metadata, onTableClick, searchText = '' }: SchemaBrowserProps) {

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

  const renderColumn = (col: ColumnMetadata) => (
    <div
      key={col.name}
      className="py-2.5 px-3 border-b border-border-light last:border-0 hover:bg-bg-secondary transition-colors duration-150"
    >
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0 flex-1">
          <span className="font-mono text-sm text-text-primary truncate">{col.name}</span>
          <Tag className="flex-shrink-0 bg-bg-tertiary text-text-secondary border-0 text-xs">
            {col.dataType.toUpperCase()}
          </Tag>
        </div>
        <div className="flex items-center gap-1 flex-shrink-0">
          {col.isPrimaryKey && (
            <Tag color="gold" className="m-0 text-xs flex items-center gap-1">
              <KeyOutlined className="text-[10px]" />
              PK
            </Tag>
          )}
          {col.isForeignKey && (
            <Tag color="green" className="m-0 text-xs flex items-center gap-1">
              <LinkOutlined className="text-[10px]" />
              FK
            </Tag>
          )}
          {!col.isNullable && (
            <Tag color="red" className="m-0 text-xs">NOT NULL</Tag>
          )}
        </div>
      </div>
    </div>
  );

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
        <TableOutlined className="text-accent-blue text-sm" />
        <span className="font-mono text-sm font-medium text-text-primary group-hover:text-accent-blue transition-colors">
          {table.tableName}
        </span>
        <span className="text-xs text-text-tertiary ml-auto">
          {table.columns.length} 列
        </span>
      </div>
    ),
    children: (
      <div className="bg-white border border-border-light rounded-lg overflow-hidden mt-1 shadow-xs">
        {table.columns.map(renderColumn)}
      </div>
    ),
  }));

  const viewItems = filteredViews.map((view) => ({
    key: `view-${view.tableName}`,
    label: (
      <div className="flex items-center gap-2 py-0.5">
        <EyeOutlined className="text-accent-green text-sm" />
        <span className="font-mono text-sm font-medium text-text-primary">
          {view.tableName}
        </span>
        <span className="text-xs text-text-tertiary ml-auto">
          {view.columns.length} 列
        </span>
      </div>
    ),
    children: (
      <div className="bg-white border border-border-light rounded-lg overflow-hidden mt-1 shadow-xs">
        {view.columns.map(renderColumn)}
      </div>
    ),
  }));

  // Get all keys for default expanded state
  const allTableKeys = filteredTables.map((t) => `table-${t.tableName}`);
  const allViewKeys = filteredViews.map((v) => `view-${v.tableName}`);

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
                  <span className="text-xs font-medium text-accent-primary bg-accent-primary/10 px-2 py-0.5 rounded-full">
                    {filteredTables.length}
                  </span>
                </div>
                <Collapse
                  items={tableItems}
                  defaultActiveKey={allTableKeys}
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
                  <span className="text-xs font-medium text-accent-green bg-accent-green/10 px-2 py-0.5 rounded-full">
                    {filteredViews.length}
                  </span>
                </div>
                <Collapse
                  items={viewItems}
                  defaultActiveKey={allViewKeys}
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
