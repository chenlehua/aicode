import { Tag } from '@/types'
import { TagBadge } from '@/components/tags/TagBadge'
import { Checkbox } from '@/components/ui/checkbox'
import { Button } from '@/components/ui/button'
import { Plus } from 'lucide-react'

interface TagFilterProps {
  tags: Tag[]
  selectedTagIds: string[]
  onChange: (tagIds: string[]) => void
  onNewTag: () => void
}

export function TagFilter({ tags, selectedTagIds, onChange, onNewTag }: TagFilterProps) {
  const handleTagToggle = (tagId: string) => {
    if (selectedTagIds.includes(tagId)) {
      onChange(selectedTagIds.filter(id => id !== tagId))
    } else {
      onChange([...selectedTagIds, tagId])
    }
  }

  const handleSelectAll = () => {
    if (selectedTagIds.length === tags.length) {
      onChange([])
    } else {
      onChange(tags.map(tag => tag.id))
    }
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="text-sm font-semibold text-foreground/80 tracking-tight">标签筛选</div>
        {tags.length > 0 && (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleSelectAll}
            className="h-7 text-xs rounded-lg hover:bg-muted/50"
          >
            {selectedTagIds.length === tags.length ? '取消全选' : '全选'}
          </Button>
        )}
      </div>
      <div className="space-y-1.5 max-h-80 overflow-y-auto pr-1">
        {tags.length === 0 ? (
          <div className="text-sm text-muted-foreground py-6 text-center">暂无标签</div>
        ) : (
          tags.map(tag => (
            <div
              key={tag.id}
              className="flex items-center gap-3 p-2.5 rounded-xl hover:bg-muted/50 cursor-pointer transition-all duration-200 group"
              onClick={() => handleTagToggle(tag.id)}
            >
              <Checkbox
                checked={selectedTagIds.includes(tag.id)}
                onCheckedChange={() => handleTagToggle(tag.id)}
                className="transition-transform duration-200 group-hover:scale-110"
              />
              <TagBadge tag={tag} />
              {tag.ticketCount !== undefined && (
                <span className="text-xs font-medium text-muted-foreground ml-auto">
                  {tag.ticketCount}
                </span>
              )}
            </div>
          ))
        )}
      </div>
      <Button
        variant="outline"
        size="sm"
        className="w-full gap-2 h-10 rounded-xl border-dashed hover:border-primary/50 hover:bg-primary/5 transition-all duration-200"
        onClick={onNewTag}
      >
        <Plus className="h-4 w-4" />
        新建标签
      </Button>
    </div>
  )
}
