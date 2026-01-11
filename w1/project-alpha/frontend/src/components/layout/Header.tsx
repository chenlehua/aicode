import { Button } from '@/components/ui/button'
import { Plus } from 'lucide-react'
import { TicketSearch } from '@/components/tickets/TicketSearch'

interface HeaderProps {
  search: string
  onSearchChange: (value: string) => void
  onNewTicket: () => void
}

export function Header({ search, onSearchChange, onNewTicket }: HeaderProps) {
  return (
    <header className="sticky top-0 z-50 border-b border-border/50 bg-background/80 backdrop-blur-xl glass">
      <div className="container mx-auto flex flex-col md:flex-row h-auto md:h-20 items-stretch md:items-center gap-4 md:gap-6 px-6 py-4 md:py-0">
        <div className="flex items-center justify-between md:justify-start gap-3 flex-shrink-0">
          <h1 className="text-xl md:text-3xl font-semibold tracking-tight bg-gradient-to-r from-foreground to-foreground/80 bg-clip-text text-transparent">
            Ticket Tag Management
          </h1>
          <Button onClick={onNewTicket} className="gap-2 md:hidden" size="sm">
            <Plus className="h-4 w-4" />
            <span>新建</span>
          </Button>
        </div>
        <div className="flex-1 max-w-2xl md:mx-auto order-3 md:order-2">
          <TicketSearch value={search} onChange={onSearchChange} />
        </div>
        <div className="hidden md:flex flex-shrink-0 order-2 md:order-3">
          <Button onClick={onNewTicket} className="gap-2" size="default">
            <Plus className="h-4 w-4" />
            <span className="hidden sm:inline">新建 Ticket</span>
            <span className="sm:hidden">新建</span>
          </Button>
        </div>
      </div>
    </header>
  )
}
