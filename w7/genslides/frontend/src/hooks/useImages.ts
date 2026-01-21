/**
 * Hook for image management
 */

import { useCallback } from "react";
import { imagesApi } from "@/api";
import { useUIStore, useSlidesStore } from "@/stores";
import { logger } from "@/utils";

export function useImages(slug: string) {
  const { addToast, addGeneratingSlide, removeGeneratingSlide, isSlideGenerating } =
    useUIStore();

  // Generate image for a slide
  const generateImage = useCallback(
    async (sid: string, force = false) => {
      if (isSlideGenerating(sid)) {
        logger.warn("Slide is already generating:", sid);
        return;
      }

      addGeneratingSlide(sid);

      try {
        const response = await imagesApi.generateImage(slug, sid, force);
        logger.info("Generation task started:", response.task_id);
        // The actual image will be updated via WebSocket
      } catch (err) {
        removeGeneratingSlide(sid);
        addToast({
          type: "error",
          message: "Failed to start image generation",
        });
        logger.error("Failed to generate image:", err);
      }
    },
    [slug, addToast, addGeneratingSlide, removeGeneratingSlide, isSlideGenerating]
  );

  // Get images for a slide
  const getImages = useCallback(
    async (sid: string) => {
      try {
        return await imagesApi.getImages(slug, sid);
      } catch (err) {
        logger.error("Failed to get images:", err);
        return null;
      }
    },
    [slug]
  );

  return {
    generateImage,
    getImages,
    isSlideGenerating,
  };
}
