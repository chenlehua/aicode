/**
 * Hook for keyboard shortcuts
 */

import { useEffect, useCallback } from "react";
import { usePlayerStore, useSlidesStore } from "@/stores";

interface KeyboardOptions {
  enabled?: boolean;
  onCreateSlide?: (afterSid?: string) => void;
}

export function useKeyboard(options: KeyboardOptions = {}) {
  const { enabled = true, onCreateSlide } = options;

  const { slides, selectedSid, selectSlide } = useSlidesStore();
  const { isFullscreen, isPlaying, next, prev, exitFullscreen, pause, play } =
    usePlayerStore();

  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      // Ignore if typing in input/textarea
      const target = event.target as HTMLElement;
      if (
        target.tagName === "INPUT" ||
        target.tagName === "TEXTAREA" ||
        target.isContentEditable
      ) {
        return;
      }

      // Player controls
      if (isFullscreen) {
        switch (event.key) {
          case "Escape":
            exitFullscreen();
            break;
          case "ArrowRight":
          case " ":
            event.preventDefault();
            next();
            break;
          case "ArrowLeft":
            event.preventDefault();
            prev();
            break;
          case "p":
            event.preventDefault();
            if (isPlaying) {
              pause();
            } else {
              play();
            }
            break;
        }
        return;
      }

      // Editor controls
      const currentIndex = slides.findIndex((s) => s.sid === selectedSid);

      switch (event.key) {
        case "ArrowUp":
          if (event.metaKey || event.ctrlKey) {
            event.preventDefault();
            if (currentIndex > 0) {
              selectSlide(slides[currentIndex - 1]!.sid);
            }
          }
          break;
        case "ArrowDown":
          if (event.metaKey || event.ctrlKey) {
            event.preventDefault();
            if (currentIndex < slides.length - 1) {
              selectSlide(slides[currentIndex + 1]!.sid);
            }
          }
          break;
        case "Enter":
          // Create new slide after selected slide when Enter is pressed
          // Only trigger if a slide is actually selected (user clicked on it)
          if (onCreateSlide && selectedSid) {
            event.preventDefault();
            onCreateSlide(selectedSid);
          }
          break;
      }
    },
    [
      isFullscreen,
      isPlaying,
      slides,
      selectedSid,
      selectSlide,
      next,
      prev,
      exitFullscreen,
      pause,
      play,
      onCreateSlide,
    ]
  );

  useEffect(() => {
    if (!enabled) return;

    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [enabled, handleKeyDown]);
}
