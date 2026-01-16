/** Component for natural language query input. */

import { Input } from 'antd';

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
  placeholder = 'DESCRIBE YOUR QUERY IN NATURAL LANGUAGE (English or Chinese)',
  disabled = false,
}: NaturalLanguageInputProps) {
  return (
    <TextArea
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      disabled={disabled}
      showCount
      maxLength={1000}
      className="rounded-lg font-mono text-sm h-full"
      style={{ fontFamily: 'inherit', resize: 'none', height: '100%' }}
    />
  );
}
