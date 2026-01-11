import { ReactNode } from 'react'
import { Header } from './Header'
import { Sidebar } from './Sidebar'
import { Tag } from '@/types'
import { TicketStatus } from '@/components/filters/StatusFilter'

interface MainLayoutProps {
  children: ReactNode
  search: string
  onSearchChange: (value: string) => void
  status: TicketStatus
  onStatusChange: (status: TicketStatus) => void
  tags: Tag[]
  selectedTagIds: string[]
  onTagIdsChange: (tagIds: string[]) => void
  onNewTicket: () => void
  onNewTag: () => void
}

export function MainLayout({
  children,
  search,
  onSearchChange,
  status,
  onStatusChange,
  tags,
  selectedTagIds,
  onTagIdsChange,
  onNewTicket,
  onNewTag,
}: MainLayoutProps) {
  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-b from-background to-muted/20">
      <Header search={search} onSearchChange={onSearchChange} onNewTicket={onNewTicket} />
      <div className="flex flex-1 overflow-hidden flex-col md:flex-row">
        <Sidebar
          status={status}
          onStatusChange={onStatusChange}
          tags={tags}
          selectedTagIds={selectedTagIds}
          onTagIdsChange={onTagIdsChange}
          onNewTag={onNewTag}
        />
        <main className="flex-1 overflow-y-auto p-6 md:p-8 lg:p-12">
          <div className="max-w-6xl mx-auto">{children}</div>
        </main>
      </div>
    </div>
  )
}
