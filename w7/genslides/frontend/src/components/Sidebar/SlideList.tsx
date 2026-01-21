/**
 * Slide list component
 */

import { SlideItem } from "./SlideItem";
import type { Slide } from "@/types";
import { useUIStore } from "@/stores";

interface SlideListProps {
  slides: Slide[];
  selectedSid: string | null;
  onSelect: (sid: string) => void;
  onDelete: (sid: string) => void;
  onContentChange: (sid: string, content: string) => void;
}

export function SlideList({
  slides,
  selectedSid,
  onSelect,
  onDelete,
  onContentChange,
}: SlideListProps): JSX.Element {
  const { isSlideGenerating } = useUIStore();

  if (slides.length === 0) {
    return (
      <div className="flex h-32 items-center justify-center text-sm text-[var(--md-slate)]">
        No slides yet
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      {slides.map((slide, index) => (
        <SlideItem
          key={slide.sid}
          slide={slide}
          index={index}
          isSelected={slide.sid === selectedSid}
          isGenerating={isSlideGenerating(slide.sid)}
          onSelect={onSelect}
          onDelete={onDelete}
          onContentChange={onContentChange}
        />
      ))}
    </div>
  );
}
