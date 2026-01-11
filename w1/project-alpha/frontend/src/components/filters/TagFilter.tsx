import { Tag } from "@/types";
import { TagBadge } from "@/components/tags/TagBadge";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";

interface TagFilterProps {
  tags: Tag[];
  selectedTagIds: string[];
  onChange: (tagIds: string[]) => void;
  onNewTag: () => void;
}

export function TagFilter({
  tags,
  selectedTagIds,
  onChange,
  onNewTag,
}: TagFilterProps) {
  const handleTagToggle = (tagId: string) => {
    if (selectedTagIds.includes(tagId)) {
      onChange(selectedTagIds.filter((id) => id !== tagId));
    } else {
      onChange([...selectedTagIds, tagId]);
    }
  };

  const handleSelectAll = () => {
    if (selectedTagIds.length === tags.length) {
      onChange([]);
    } else {
      onChange(tags.map((tag) => tag.id));
    }
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="text-sm font-medium">标签筛选</div>
        {tags.length > 0 && (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleSelectAll}
            className="h-6 text-xs"
          >
            {selectedTagIds.length === tags.length ? "取消全选" : "全选"}
          </Button>
        )}
      </div>
      <div className="space-y-2 max-h-64 overflow-y-auto">
        {tags.length === 0 ? (
          <div className="text-sm text-muted-foreground py-4 text-center">
            暂无标签
          </div>
        ) : (
          tags.map((tag) => (
            <div
              key={tag.id}
              className="flex items-center gap-2 p-2 rounded-md hover:bg-accent cursor-pointer"
              onClick={() => handleTagToggle(tag.id)}
            >
              <Checkbox
                checked={selectedTagIds.includes(tag.id)}
                onCheckedChange={() => handleTagToggle(tag.id)}
              />
              <TagBadge tag={tag} />
              {tag.ticketCount !== undefined && (
                <span className="text-xs text-muted-foreground ml-auto">
                  ({tag.ticketCount})
                </span>
              )}
            </div>
          ))
        )}
      </div>
      <Button
        variant="outline"
        size="sm"
        className="w-full gap-2"
        onClick={onNewTag}
      >
        <Plus className="h-4 w-4" />
        新建标签
      </Button>
    </div>
  );
}
