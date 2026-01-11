import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { TicketSearch } from "@/components/tickets/TicketSearch";

interface HeaderProps {
  search: string;
  onSearchChange: (value: string) => void;
  onNewTicket: () => void;
}

export function Header({ search, onSearchChange, onNewTicket }: HeaderProps) {
  return (
    <header className="border-b bg-background">
      <div className="container mx-auto flex flex-col md:flex-row h-auto md:h-16 items-stretch md:items-center gap-3 md:gap-4 px-4 py-3 md:py-0">
        <div className="flex items-center justify-between md:justify-start gap-2 flex-shrink-0">
          <h1 className="text-lg md:text-2xl font-bold">
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
          <Button onClick={onNewTicket} className="gap-2" size="sm">
            <Plus className="h-4 w-4" />
            <span className="hidden sm:inline">新建 Ticket</span>
            <span className="sm:hidden">新建</span>
          </Button>
        </div>
      </div>
    </header>
  );
}
