/** Schema browser component with search functionality. */

import { useMemo } from 'react';
import { Collapse, Tag, Empty } from 'antd';
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
    <div key={col.name} className="py-2 px-3 border-b border-gray-100 last:border-0 hover:bg-gray-50">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="font-mono text-sm text-gray-800">{col.name}</span>
          <Tag className="m-0 text-xs border-gray-300 text-gray-500">{col.dataType.toUpperCase()}</Tag>
          {col.isPrimaryKey && <Tag color="blue" className="m-0 text-xs">PK</Tag>}
          {col.isForeignKey && <Tag color="green" className="m-0 text-xs">FK</Tag>}
        </div>
        {!col.isNullable && <Tag color="red" className="m-0 text-xs">NOT NULL</Tag>}
      </div>
    </div>
  );

  const tableItems = filteredTables.map((table) => ({
    key: `table-${table.tableName}`,
    label: (
      <div
        className="flex items-center cursor-pointer group"
        onClick={(e) => {
          e.stopPropagation();
          onTableClick?.(table.tableName);
        }}
      >
        <span className="font-mono text-sm font-medium text-gray-800 group-hover:text-blue-600">
          {table.tableName}
        </span>
      </div>
    ),
    children: (
      <div className="bg-white border border-gray-200 rounded-md overflow-hidden">
        {table.columns.map(renderColumn)}
      </div>
    ),
  }));

  const viewItems = filteredViews.map((view) => ({
    key: `view-${view.tableName}`,
    label: (
      <div className="flex items-center">
        <span className="font-mono text-sm font-medium text-gray-800">{view.tableName}</span>
      </div>
    ),
    children: (
      <div className="bg-white border border-gray-200 rounded-md overflow-hidden">
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
              <span className="text-gray-500 text-sm">
                {searchText ? '未找到匹配的表或视图' : '暂无表或视图'}
              </span>
            }
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            className="py-8"
          />
        ) : (
          <div className="space-y-4">
            {filteredTables.length > 0 && (
              <div>
                <div className="mb-2 pb-2 border-b border-gray-100">
                  <span className="text-sm font-semibold text-gray-700">
                    Tables ({filteredTables.length})
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
                <div className="mb-2 pb-2 border-b border-gray-100">
                  <span className="text-sm font-semibold text-gray-700">
                    Views ({filteredViews.length})
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
