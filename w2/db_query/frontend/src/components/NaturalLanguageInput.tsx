/** Component for natural language query input. */

import { Input } from 'antd';
import { MessageOutlined } from '@ant-design/icons';

const { TextArea } = Input;

interface NaturalLanguageInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
}

export function NaturalLanguageInput({
  value,
  onChange,
  placeholder = '用自然语言描述您的查询需求（支持中文和英文）',
  disabled = false,
}: NaturalLanguageInputProps) {
  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center gap-2 mb-3">
        <MessageOutlined className="text-accent-primary" />
        <span className="text-xs font-semibold text-text-secondary uppercase tracking-wide">
          自然语言查询
        </span>
      </div>
      <TextArea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        showCount
        maxLength={1000}
        className="flex-1 rounded-xl text-base resize-none border-border-light focus:border-accent-primary focus:shadow-[0_0_0_2px_rgba(255,204,0,0.2)]"
        style={{
          fontFamily: 'Inter, sans-serif',
          resize: 'none',
          minHeight: '120px',
        }}
      />
      <p className="text-xs text-text-tertiary mt-2">
        💡 提示：使用具体的表名和条件可以获得更准确的 SQL 结果
      </p>
    </div>
  );
}
