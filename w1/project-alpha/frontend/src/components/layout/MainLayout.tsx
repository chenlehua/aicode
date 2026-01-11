import { ReactNode } from "react";
import { Header } from "./Header";
import { Sidebar } from "./Sidebar";
import { Tag } from "@/types";
import { TicketStatus } from "@/components/filters/StatusFilter";

interface MainLayoutProps {
  children: ReactNode;
  search: string;
  onSearchChange: (value: string) => void;
  status: TicketStatus;
  onStatusChange: (status: TicketStatus) => void;
  tags: Tag[];
  selectedTagIds: string[];
  onTagIdsChange: (tagIds: string[]) => void;
  onNewTicket: () => void;
  onNewTag: () => void;
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
    <div className="min-h-screen flex flex-col">
      <Header
        search={search}
        onSearchChange={onSearchChange}
        onNewTicket={onNewTicket}
      />
      <div className="flex flex-1 overflow-hidden flex-col md:flex-row">
        <Sidebar
          status={status}
          onStatusChange={onStatusChange}
          tags={tags}
          selectedTagIds={selectedTagIds}
          onTagIdsChange={onTagIdsChange}
          onNewTag={onNewTag}
        />
        <main className="flex-1 overflow-y-auto p-4 md:p-6">{children}</main>
      </div>
    </div>
  );
}
