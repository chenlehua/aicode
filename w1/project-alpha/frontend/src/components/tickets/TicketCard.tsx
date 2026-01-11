import { Ticket } from '@/types'
import { Card } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import { Button } from '@/components/ui/button'
import { TagBadge } from '@/components/tags/TagBadge'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { MoreVertical, Edit, Trash2 } from 'lucide-react'
import { cn, formatDate } from '@/lib/utils'

interface TicketCardProps {
  ticket: Ticket
  onComplete: (id: string) => void
  onReopen: (id: string) => void
  onEdit: (id: string) => void
  onDelete: (id: string) => void
  isSelected?: boolean
  onSelectChange?: (id: string, selected: boolean) => void
  showSelection?: boolean
}

export function TicketCard({
  ticket,
  onComplete,
  onReopen,
  onEdit,
  onDelete,
  isSelected = false,
  onSelectChange,
  showSelection = false,
}: TicketCardProps) {
  const isCompleted = ticket.status === 'completed'

  const handleToggleStatus = () => {
    if (isCompleted) {
      onReopen(ticket.id)
    } else {
      onComplete(ticket.id)
    }
  }

  const handleSelectionChange = (checked: boolean | 'indeterminate') => {
    if (checked === 'indeterminate') return
    onSelectChange?.(ticket.id, checked)
  }

  return (
    <Card
      className={cn(
        'p-6 transition-all duration-300 animate-fade-in group',
        isCompleted && 'opacity-60',
        isSelected && 'ring-2 ring-primary ring-offset-2'
      )}
    >
      <div className="flex items-start gap-4">
        {showSelection ? (
          <Checkbox
            checked={isSelected}
            onCheckedChange={handleSelectionChange}
            className="mt-1.5 transition-transform duration-200 hover:scale-110"
            onClick={e => e.stopPropagation()}
          />
        ) : (
          <Checkbox
            checked={isCompleted}
            onCheckedChange={handleToggleStatus}
            className="mt-1.5 transition-transform duration-200 hover:scale-110"
          />
        )}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-3">
            <h3
              className={cn(
                'font-semibold text-lg md:text-xl break-words leading-tight tracking-tight',
                isCompleted && 'line-through text-muted-foreground'
              )}
            >
              {ticket.title}
            </h3>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-9 w-9 opacity-0 group-hover:opacity-100 transition-opacity duration-200 rounded-full"
                >
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem
                  onClick={() => onEdit(ticket.id)}
                  onKeyDown={e => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault()
                      onEdit(ticket.id)
                    }
                  }}
                >
                  <Edit className="mr-2 h-4 w-4" />
                  编辑
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={() => onDelete(ticket.id)}
                  onKeyDown={e => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault()
                      onDelete(ticket.id)
                    }
                  }}
                  className="text-destructive"
                >
                  <Trash2 className="mr-2 h-4 w-4" />
                  删除
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
          {ticket.description && (
            <p
              className={cn(
                'text-sm text-muted-foreground mt-3 leading-relaxed line-clamp-2',
                isCompleted && 'line-through'
              )}
            >
              {ticket.description}
            </p>
          )}
          <div className="flex items-center gap-2 mt-4 flex-wrap">
            {ticket.tags.map(tag => (
              <TagBadge key={tag.id} tag={tag} />
            ))}
          </div>
          <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 mt-4 text-xs text-muted-foreground">
            <span className="font-medium">创建于 {formatDate(ticket.createdAt)}</span>
            {ticket.completedAt && (
              <span className="font-medium">完成于 {formatDate(ticket.completedAt)}</span>
            )}
          </div>
        </div>
      </div>
    </Card>
  )
}
