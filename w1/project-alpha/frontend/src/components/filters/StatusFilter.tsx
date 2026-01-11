import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

export type TicketStatus = 'all' | 'open' | 'completed'

interface StatusFilterProps {
  value: TicketStatus
  onChange: (status: TicketStatus) => void
}

const statusOptions: { value: TicketStatus; label: string }[] = [
  { value: 'all', label: '所有' },
  { value: 'open', label: '进行中' },
  { value: 'completed', label: '已完成' },
]

export function StatusFilter({ value, onChange }: StatusFilterProps) {
  return (
    <div className="space-y-3">
      <div className="text-sm font-semibold text-foreground/80 tracking-tight">状态筛选</div>
      <div className="flex flex-col gap-2">
        {statusOptions.map(option => (
          <Button
            key={option.value}
            variant={value === option.value ? 'default' : 'ghost'}
            className={cn(
              'w-full justify-start h-11 rounded-xl transition-all duration-200',
              value === option.value
                ? 'bg-primary text-primary-foreground shadow-sm'
                : 'hover:bg-muted/50'
            )}
            onClick={() => onChange(option.value)}
          >
            {option.label}
          </Button>
        ))}
      </div>
    </div>
  )
}
