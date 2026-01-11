import { StatusFilter } from "@/components/filters/StatusFilter";
import { TagFilter } from "@/components/filters/TagFilter";
import { Tag } from "@/types";
import { TicketStatus } from "@/components/filters/StatusFilter";

interface SidebarProps {
  status: TicketStatus;
  onStatusChange: (status: TicketStatus) => void;
  tags: Tag[];
  selectedTagIds: string[];
  onTagIdsChange: (tagIds: string[]) => void;
  onNewTag: () => void;
}

export function Sidebar({
  status,
  onStatusChange,
  tags,
  selectedTagIds,
  onTagIdsChange,
  onNewTag,
}: SidebarProps) {
  return (
    <aside className="w-full md:w-64 border-r bg-background p-4 space-y-6 overflow-y-auto">
      <div className="space-y-4">
        <StatusFilter value={status} onChange={onStatusChange} />
        <TagFilter
          tags={tags}
          selectedTagIds={selectedTagIds}
          onChange={onTagIdsChange}
          onNewTag={onNewTag}
        />
      </div>
    </aside>
  );
}
