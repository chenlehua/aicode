/**
 * Editable title input component
 */

import { useState, useCallback, useEffect } from "react";
import { useDebounce } from "@/hooks";
import { cn } from "@/utils";

interface TitleInputProps {
  title: string;
  onTitleChange: (title: string) => void;
}

export function TitleInput({ title, onTitleChange }: TitleInputProps): JSX.Element {
  const [value, setValue] = useState(title);
  const [isEditing, setIsEditing] = useState(false);
  const debouncedValue = useDebounce(value, 500);

  // Sync with prop
  useEffect(() => {
    setValue(title);
  }, [title]);

  // Save on debounced change
  useEffect(() => {
    if (debouncedValue !== title && debouncedValue.trim()) {
      onTitleChange(debouncedValue);
    }
  }, [debouncedValue, title, onTitleChange]);

  const handleBlur = useCallback(() => {
    setIsEditing(false);
    if (value.trim() && value !== title) {
      onTitleChange(value);
    }
  }, [value, title, onTitleChange]);

  return (
    <input
      type="text"
      value={value}
      onChange={(e) => setValue(e.target.value)}
      onFocus={() => setIsEditing(true)}
      onBlur={handleBlur}
      className={cn(
        "bg-transparent font-bold uppercase tracking-wider text-[var(--md-ink)]",
        "border-b-2 border-transparent px-1 py-0.5",
        "focus:border-[var(--md-sky-strong)] focus:outline-none",
        "transition-colors duration-200",
        isEditing && "border-[var(--md-sky)]"
      )}
      placeholder="Untitled"
      aria-label="Project title"
    />
  );
}
