import { Tag } from "@/types";
import { TagBadge } from "./TagBadge";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Plus } from "lucide-react";

interface TagSelectorProps {
  tags: Tag[];
  selectedTagIds: string[];
  onChange: (tagIds: string[]) => void;
  onNewTag?: () => void;
  allowCreate?: boolean;
}

export function TagSelector({
  tags,
  selectedTagIds,
  onChange,
  onNewTag,
  allowCreate = true,
}: TagSelectorProps) {
  const handleTagToggle = (tagId: string) => {
    if (selectedTagIds.includes(tagId)) {
      onChange(selectedTagIds.filter((id) => id !== tagId));
    } else {
      onChange([...selectedTagIds, tagId]);
    }
  };

  return (
    <div className="space-y-3">
      <div className="text-sm font-medium">标签</div>
      <div className="flex flex-wrap gap-2">
        {tags.map((tag) => (
          <div
            key={tag.id}
            className="flex items-center gap-2 cursor-pointer"
            onClick={() => handleTagToggle(tag.id)}
          >
            <Checkbox
              checked={selectedTagIds.includes(tag.id)}
              onCheckedChange={() => handleTagToggle(tag.id)}
            />
            <TagBadge tag={tag} />
          </div>
        ))}
      </div>
      {allowCreate && onNewTag && (
        <Button
          type="button"
          variant="outline"
          size="sm"
          className="gap-2"
          onClick={onNewTag}
        >
          <Plus className="h-4 w-4" />
          新建标签
        </Button>
      )}
    </div>
  );
}
