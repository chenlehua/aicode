import { Button } from '@/components/ui/button'
import { ArrowUp, ArrowDown } from 'lucide-react'
import { cn } from '@/lib/utils'

export type SortField = 'created_at' | 'updated_at' | 'completed_at' | 'title'
export type SortOrder = 'asc' | 'desc'

interface SortFilterProps {
  sortBy: SortField
  sortOrder: SortOrder
  onChange: (sortBy: SortField, sortOrder: SortOrder) => void
}

const sortOptions: { value: SortField; label: string }[] = [
  { value: 'created_at', label: '创建时间' },
  { value: 'updated_at', label: '更新时间' },
  { value: 'completed_at', label: '完成时间' },
  { value: 'title', label: '标题' },
]

export function SortFilter({ sortBy, sortOrder, onChange }: SortFilterProps) {
  const handleSortChange = (field: SortField) => {
    if (field === sortBy) {
      // Toggle order if same field
      onChange(field, sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      // Set new field with default desc order
      onChange(field, 'desc')
    }
  }

  return (
    <div className="space-y-3">
      <div className="text-sm font-semibold text-foreground/80 tracking-tight">排序方式</div>
      <div className="flex flex-col gap-2">
        {sortOptions.map(option => {
          const isActive = sortBy === option.value
          return (
            <Button
              key={option.value}
              variant={isActive ? 'default' : 'ghost'}
              className={cn(
                'w-full justify-start h-11 rounded-xl transition-all duration-200',
                isActive ? 'bg-primary text-primary-foreground shadow-sm' : 'hover:bg-muted/50'
              )}
              onClick={() => handleSortChange(option.value)}
            >
              <span className="flex-1 text-left">{option.label}</span>
              {isActive && (
                <span className="ml-2">
                  {sortOrder === 'asc' ? (
                    <ArrowUp className="h-4 w-4" />
                  ) : (
                    <ArrowDown className="h-4 w-4" />
                  )}
                </span>
              )}
            </Button>
          )
        })}
      </div>
    </div>
  )
}
