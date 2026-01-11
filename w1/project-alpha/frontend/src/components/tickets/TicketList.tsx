import { useState, useEffect } from 'react'
import { Ticket } from '@/types'
import { TicketCard } from './TicketCard'
import { Card } from '@/components/ui/card'
import { TicketListSkeleton } from './TicketListSkeleton'
import { BatchActionsBar } from './BatchActionsBar'
import { TicketListToolbar } from './TicketListToolbar'
import { SortField, SortOrder } from '@/components/filters/SortFilter'

interface TicketListProps {
  tickets: Ticket[]
  isLoading?: boolean
  onComplete: (id: string) => void
  onReopen: (id: string) => void
  onEdit: (id: string) => void
  onDelete: (id: string) => void
  onBatchComplete?: (ids: string[]) => void
  onBatchDelete?: (ids: string[]) => void
  isBatchLoading?: boolean
  onEnterBatchMode?: () => void
  sortBy?: SortField
  sortOrder?: SortOrder
  onSortChange?: (sortBy: SortField, sortOrder: SortOrder) => void
}

export function TicketList({
  tickets,
  isLoading,
  onComplete,
  onReopen,
  onEdit,
  onDelete,
  onBatchComplete,
  onBatchDelete,
  isBatchLoading = false,
  onEnterBatchMode,
  sortBy = 'created_at',
  sortOrder = 'desc',
  onSortChange,
}: TicketListProps) {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
  const [isSelectionMode, setIsSelectionMode] = useState(false)

  const handleSelectAll = () => {
    if (selectedIds.size === tickets.length) {
      setSelectedIds(new Set())
      setIsSelectionMode(false)
    } else {
      setSelectedIds(new Set(tickets.map(t => t.id)))
      setIsSelectionMode(true)
    }
  }

  const handleClearSelection = () => {
    setSelectedIds(new Set())
    setIsSelectionMode(false)
  }

  const handleBatchComplete = () => {
    const ids = Array.from(selectedIds)
    if (ids.length === 0) return
    onBatchComplete?.(ids)
    // Don't clear selection here - let the parent handle it after success
  }

  const handleBatchDelete = () => {
    const ids = Array.from(selectedIds)
    if (ids.length === 0) return
    onBatchDelete?.(ids)
    // Don't clear selection here - let the parent handle it after success
  }

  // Enable selection mode when user starts selecting
  const handleFirstSelect = (id: string, selected: boolean) => {
    setSelectedIds(prev => {
      const next = new Set(prev)
      if (selected) {
        next.add(id)
        // Enter selection mode when first item is selected
        if (!isSelectionMode) {
          setIsSelectionMode(true)
        }
      } else {
        next.delete(id)
        // Exit selection mode if no items are selected
        if (next.size === 0) {
          setIsSelectionMode(false)
        }
      }
      return next
    })
  }

  // Clear selection when batch operations complete successfully
  useEffect(() => {
    if (!isBatchLoading && selectedIds.size > 0) {
      // Check if any selected tickets still exist in the list
      const existingIds = new Set(tickets.map(t => t.id))
      const stillSelected = Array.from(selectedIds).filter(id => existingIds.has(id))

      // If no selected tickets exist anymore, clear selection
      if (stillSelected.length === 0) {
        setSelectedIds(new Set())
        setIsSelectionMode(false)
      } else if (stillSelected.length < selectedIds.size) {
        // Otherwise, update selection to only include existing tickets
        setSelectedIds(new Set(stillSelected))
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tickets, isBatchLoading])

  if (isLoading) {
    return <TicketListSkeleton />
  }

  if (tickets.length === 0) {
    return (
      <Card className="p-16 text-center animate-fade-in">
        <div className="flex flex-col items-center gap-3">
          <div className="w-16 h-16 rounded-full bg-muted/50 flex items-center justify-center">
            <svg
              className="w-8 h-8 text-muted-foreground"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          </div>
          <p className="text-lg font-medium text-muted-foreground">暂无 Ticket</p>
          <p className="text-sm text-muted-foreground/70">创建你的第一个 Ticket 开始使用</p>
        </div>
      </Card>
    )
  }

  const showSelection = isSelectionMode || selectedIds.size > 0
  const allSelected = selectedIds.size === tickets.length && tickets.length > 0

  const handleEnterBatchMode = () => {
    setIsSelectionMode(true)
    onEnterBatchMode?.()
  }

  return (
    <div className="space-y-4">
      {!showSelection && (
        <TicketListToolbar
          onEnterBatchMode={onBatchComplete || onBatchDelete ? handleEnterBatchMode : undefined}
          sortBy={sortBy}
          sortOrder={sortOrder}
          onSortChange={onSortChange || (() => {})}
        />
      )}
      {showSelection && (onBatchComplete || onBatchDelete) && (
        <div className="mb-2">
          <BatchActionsBar
            selectedCount={selectedIds.size}
            onComplete={handleBatchComplete}
            onDelete={handleBatchDelete}
            onClearSelection={handleClearSelection}
            isLoading={isBatchLoading}
            allSelected={allSelected}
            onSelectAll={handleSelectAll}
          />
        </div>
      )}

      <div className="space-y-4 md:space-y-5">
        {tickets.map((ticket, index) => (
          <div
            key={ticket.id}
            className="animate-fade-in"
            style={{ animationDelay: `${index * 0.05}s` }}
          >
            <TicketCard
              ticket={ticket}
              onComplete={onComplete}
              onReopen={onReopen}
              onEdit={onEdit}
              onDelete={onDelete}
              isSelected={selectedIds.has(ticket.id)}
              onSelectChange={handleFirstSelect}
              showSelection={showSelection}
            />
          </div>
        ))}
      </div>
    </div>
  )
}
