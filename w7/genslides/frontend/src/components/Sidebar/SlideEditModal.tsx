/**
 * Modal for editing slide content
 */

import { useState, useEffect, useRef } from "react";
import { Modal, Button, Textarea } from "@/components/common";

interface SlideEditModalProps {
  isOpen: boolean;
  slideIndex: number;
  content: string;
  onSave: (content: string) => void;
  onClose: () => void;
}

export function SlideEditModal({
  isOpen,
  slideIndex,
  content,
  onSave,
  onClose,
}: SlideEditModalProps): JSX.Element {
  const [editContent, setEditContent] = useState(content);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Reset content when modal opens
  useEffect(() => {
    if (isOpen) {
      setEditContent(content);
      // Focus textarea after a short delay for animation
      setTimeout(() => {
        textareaRef.current?.focus();
        textareaRef.current?.select();
      }, 100);
    }
  }, [isOpen, content]);

  const handleSave = () => {
    onSave(editContent);
    onClose();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && e.ctrlKey) {
      handleSave();
    } else if (e.key === "Escape") {
      onClose();
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={`Edit Slide ${slideIndex + 1}`}>
      <div className="flex flex-col gap-4">
        <Textarea
          ref={textareaRef}
          value={editContent}
          onChange={(e) => setEditContent(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Enter slide content..."
          className="min-h-[200px] resize-y"
          rows={8}
        />
        <p className="text-xs text-[var(--md-slate)]">
          Tip: Ctrl+Enter to save, Esc to cancel
        </p>
        <div className="flex justify-end gap-3">
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleSave}>Save</Button>
        </div>
      </div>
    </Modal>
  );
}
