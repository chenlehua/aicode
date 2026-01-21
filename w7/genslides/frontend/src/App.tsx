/**
 * Root application component
 */

import { useCallback, useMemo } from "react";
import { Header } from "@/components/Header";
import { Sidebar } from "@/components/Sidebar";
import { Preview } from "@/components/Preview";
import { FullscreenPlayer } from "@/components/Player";
import { StyleSetupModal, StyleSettingsModal } from "@/components/Modals";
import { ToastContainer, Loading, ErrorBoundary } from "@/components/common";
import { useSlides, useStyle, useWebSocket, useKeyboard, useImages } from "@/hooks";

// Get slug from URL or use default
function getSlugFromUrl(): string {
  const path = window.location.pathname;
  const match = path.match(/^\/slides\/([a-zA-Z0-9_-]+)/);
  if (match?.[1]) {
    return match[1];
  }
  // Default slug
  return "demo";
}

export function App(): JSX.Element {
  const slug = useMemo(() => getSlugFromUrl(), []);

  // Initialize hooks
  const {
    slides,
    selectedSid,
    isLoading,
    error,
    selectSlide,
    updateTitle,
    createSlide,
    updateSlideContent,
    deleteSlide,
  } = useSlides(slug);

  const { generateCandidates, saveStyle } = useStyle(slug);
  const { generateImage } = useImages(slug);

  // WebSocket connection for real-time updates
  useWebSocket(slug);

  // Keyboard shortcuts
  useKeyboard();

  // Handlers
  const handleAddSlide = useCallback(async () => {
    await createSlide("New slide content", selectedSid || undefined);
  }, [createSlide, selectedSid]);

  const handleContentChange = useCallback(
    (sid: string, content: string) => {
      updateSlideContent(sid, content);
    },
    [updateSlideContent]
  );

  const handleGenerate = useCallback(
    (sid: string) => {
      generateImage(sid);
    },
    [generateImage]
  );

  const handleGenerateCandidates = useCallback(
    async (prompt: string) => {
      await generateCandidates(prompt);
    },
    [generateCandidates]
  );

  const handleSaveStyle = useCallback(
    async (candidateId: string) => {
      await saveStyle(candidateId);
    },
    [saveStyle]
  );

  // Loading state
  if (isLoading) {
    return (
      <div className="md-shell flex h-screen items-center justify-center">
        <Loading size="lg" text="Loading project..." />
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="md-shell flex h-screen items-center justify-center">
        <div className="text-center">
          <h1 className="mb-4 text-2xl font-bold text-[var(--md-watermelon)]">
            Error Loading Project
          </h1>
          <p className="text-[var(--md-slate)]">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div className="md-shell flex h-screen flex-col">
        {/* Header */}
        <Header onTitleChange={updateTitle} />

        {/* Main content */}
        <div className="flex flex-1 overflow-hidden">
          {/* Sidebar */}
          <ErrorBoundary>
            <Sidebar
              slides={slides}
              selectedSid={selectedSid}
              onSelect={selectSlide}
              onDelete={deleteSlide}
              onAddSlide={handleAddSlide}
              onContentChange={handleContentChange}
            />
          </ErrorBoundary>

          {/* Preview area */}
          <main className="flex-1 overflow-hidden">
            <ErrorBoundary>
              <Preview onGenerate={handleGenerate} />
            </ErrorBoundary>
          </main>
        </div>

        {/* Fullscreen player */}
        <FullscreenPlayer />

        {/* Modals */}
        <StyleSetupModal
          slug={slug}
          onGenerateCandidates={handleGenerateCandidates}
          onSaveStyle={handleSaveStyle}
        />
        <StyleSettingsModal
          slug={slug}
          onGenerateCandidates={handleGenerateCandidates}
          onSaveStyle={handleSaveStyle}
        />

        {/* Toast notifications */}
        <ToastContainer />
      </div>
    </ErrorBoundary>
  );
}
