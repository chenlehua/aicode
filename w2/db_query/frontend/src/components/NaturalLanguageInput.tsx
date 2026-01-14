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
  placeholder = 'Describe what you want to query in natural language...',
  disabled = false,
}: NaturalLanguageInputProps) {
  return (
    <TextArea
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      disabled={disabled}
      rows={4}
      showCount
      maxLength={1000}
      style={{ fontFamily: 'inherit' }}
    />
  );
}
