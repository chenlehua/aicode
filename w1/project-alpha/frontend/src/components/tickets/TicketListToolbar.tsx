import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react'
import { SortField, SortOrder } from '@/components/filters/SortFilter'

interface TicketListToolbarProps {
  onEnterBatchMode?: () => void
  sortBy: SortField
  sortOrder: SortOrder
  onSortChange: (sortBy: SortField, sortOrder: SortOrder) => void
}

const sortOptions: { value: SortField; label: string }[] = [
  { value: 'created_at', label: '创建时间' },
  { value: 'updated_at', label: '更新时间' },
  { value: 'completed_at', label: '完成时间' },
  { value: 'title', label: '标题' },
]

export function TicketListToolbar({
  onEnterBatchMode,
  sortBy,
  sortOrder,
  onSortChange,
}: TicketListToolbarProps) {
  const currentSortOption = sortOptions.find(opt => opt.value === sortBy)
  const sortLabel = currentSortOption
    ? `${currentSortOption.label} ${sortOrder === 'asc' ? '↑' : '↓'}`
    : '排序'

  const handleSortSelect = (field: SortField) => {
    if (field === sortBy) {
      // Toggle order if same field
      onSortChange(field, sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      // Set new field with default desc order
      onSortChange(field, 'desc')
    }
  }

  return (
    <div className="flex items-center justify-between mb-4">
      <div className="flex items-center gap-2">
        {onEnterBatchMode && (
          <Button
            variant="outline"
            size="sm"
            onClick={onEnterBatchMode}
            className="gap-2 rounded-xl h-9"
          >
            <span>批量操作</span>
          </Button>
        )}
      </div>
      <div className="flex items-center gap-2">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="sm" className="gap-2 rounded-xl h-9">
              <ArrowUpDown className="h-4 w-4" />
              <span className="hidden sm:inline">{sortLabel}</span>
              <span className="sm:hidden">排序</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48">
            {sortOptions.map(option => {
              const isActive = sortBy === option.value
              return (
                <DropdownMenuItem
                  key={option.value}
                  onClick={() => handleSortSelect(option.value)}
                  className="flex items-center justify-between cursor-pointer"
                >
                  <span>{option.label}</span>
                  {isActive && (
                    <span className="ml-2">
                      {sortOrder === 'asc' ? (
                        <ArrowUp className="h-4 w-4" />
                      ) : (
                        <ArrowDown className="h-4 w-4" />
                      )}
                    </span>
                  )}
                </DropdownMenuItem>
              )
            })}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  )
}
