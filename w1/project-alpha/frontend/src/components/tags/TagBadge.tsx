import { Tag } from "@/types";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface TagBadgeProps {
  tag: Tag;
  className?: string;
  onClick?: () => void;
}

export function TagBadge({ tag, className, onClick }: TagBadgeProps) {
  return (
    <Badge
      className={cn(
        "cursor-pointer hover:opacity-80",
        onClick && "cursor-pointer",
        className,
      )}
      style={{ backgroundColor: tag.color, color: getContrastColor(tag.color) }}
      onClick={onClick}
    >
      {tag.name}
    </Badge>
  );
}

/**
 * Get contrasting text color (black or white) based on background color
 */
function getContrastColor(hexColor: string): string {
  // Remove # if present
  const hex = hexColor.replace("#", "");

  // Convert to RGB
  const r = parseInt(hex.substring(0, 2), 16);
  const g = parseInt(hex.substring(2, 4), 16);
  const b = parseInt(hex.substring(4, 6), 16);

  // Calculate luminance
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;

  // Return black or white based on luminance
  return luminance > 0.5 ? "#000000" : "#ffffff";
}
