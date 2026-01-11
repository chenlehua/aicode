import { Button } from '@/components/ui/button'
import { CheckCircle2, Trash2, X } from 'lucide-react'

interface BatchActionsBarProps {
  selectedCount: number
  onComplete: () => void
  onDelete: () => void
  onClearSelection: () => void
  isLoading?: boolean
  allSelected?: boolean
  onSelectAll?: () => void
}

export function BatchActionsBar({
  selectedCount,
  onComplete,
  onDelete,
  onClearSelection,
  isLoading = false,
  allSelected = false,
  onSelectAll,
}: BatchActionsBarProps) {
  return (
    <div className="relative z-40 mb-2">
      <div className="rounded-xl border border-primary/20 bg-primary/5 backdrop-blur-xl px-3 py-2 shadow-apple-lg animate-fade-in">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-3 flex-1 min-w-0">
            {onSelectAll && (
              <input
                type="checkbox"
                checked={allSelected}
                onChange={onSelectAll}
                className="h-4 w-4 rounded-md border-primary/30 cursor-pointer transition-all duration-200 hover:scale-110 flex-shrink-0"
              />
            )}
            <div className="flex items-center gap-2 min-w-0">
              {selectedCount > 0 ? (
                <>
                  <div className="flex h-6 w-6 items-center justify-center rounded-full bg-primary/10 text-xs font-semibold text-primary flex-shrink-0">
                    {selectedCount}
                  </div>
                  <span className="text-xs font-medium text-foreground truncate">
                    已选择 {selectedCount} 个
                  </span>
                </>
              ) : (
                <span className="text-xs font-medium text-muted-foreground">请选择 Ticket</span>
              )}
            </div>
          </div>
          <div className="flex items-center gap-1.5 flex-shrink-0">
            <Button
              variant="outline"
              size="sm"
              onClick={onComplete}
              disabled={isLoading || selectedCount === 0}
              className="gap-1.5 rounded-lg h-8 px-2.5 text-xs"
            >
              <CheckCircle2 className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">批量完成</span>
            </Button>
            <Button
              variant="destructive"
              size="sm"
              onClick={onDelete}
              disabled={isLoading || selectedCount === 0}
              className="gap-1.5 rounded-lg h-8 px-2.5 text-xs"
            >
              <Trash2 className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">批量删除</span>
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={onClearSelection}
              disabled={isLoading}
              className="h-8 w-8 rounded-full"
            >
              <X className="h-3.5 w-3.5" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
