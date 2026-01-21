/**
 * Header component
 */

import { TitleInput } from "./TitleInput";
import { StyleBadge } from "./StyleBadge";
import { CostDisplay } from "./CostDisplay";
import { PlayButton } from "./PlayButton";
import { useSlidesStore, useStyleStore, usePlayerStore } from "@/stores";

interface HeaderProps {
  onTitleChange: (title: string) => void;
}

export function Header({ onTitleChange }: HeaderProps): JSX.Element {
  const { title, slides, cost } = useSlidesStore();
  const { style, openSettingsModal, openSetupModal } = useStyleStore();
  const { play } = usePlayerStore();

  const handleStyleClick = () => {
    if (style) {
      openSettingsModal();
    } else {
      openSetupModal();
    }
  };

  const handlePlay = () => {
    if (slides.length > 0) {
      play(0);
    }
  };

  const canPlay = slides.length > 0 && slides.some((s) => s.current_image);

  return (
    <header className="md-eyebrow">
      <div className="flex items-center gap-4">
        <TitleInput title={title} onTitleChange={onTitleChange} />
        <StyleBadge style={style} onClick={handleStyleClick} />
      </div>

      <div className="flex items-center gap-4">
        <CostDisplay cost={cost} />
        <PlayButton onClick={handlePlay} disabled={!canPlay} />
      </div>
    </header>
  );
}
