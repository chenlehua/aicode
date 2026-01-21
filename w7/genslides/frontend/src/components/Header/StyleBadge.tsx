/**
 * Style badge component showing current style
 */

import { cn } from "@/utils";
import type { Style } from "@/types";

interface StyleBadgeProps {
  style: Style | null;
  onClick: () => void;
}

export function StyleBadge({ style, onClick }: StyleBadgeProps): JSX.Element {
  return (
    <button
      onClick={onClick}
      className={cn(
        "md-badge cursor-pointer transition-all hover:translate-x-0.5 hover:-translate-y-0.5",
        "hover:shadow-[-3px_3px_0_0_rgba(0,0,0,1)]",
        !style && "bg-[var(--md-fog)] border-dashed"
      )}
    >
      {style ? (
        <>
          <span className="h-4 w-4 overflow-hidden rounded-full border border-[var(--md-graphite)]">
            <img
              src={style.image}
              alt="Style"
              className="h-full w-full object-cover"
            />
          </span>
          <span className="text-xs font-bold">Style Set</span>
        </>
      ) : (
        <span className="text-xs font-bold text-[var(--md-slate)]">
          Set Style
        </span>
      )}
    </button>
  );
}
