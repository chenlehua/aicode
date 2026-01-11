import { Ticket } from "@/types";
import { TicketCard } from "./TicketCard";
import { Card } from "@/components/ui/card";
import { TicketListSkeleton } from "./TicketListSkeleton";

interface TicketListProps {
  tickets: Ticket[];
  isLoading?: boolean;
  onComplete: (id: string) => void;
  onReopen: (id: string) => void;
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
}

export function TicketList({
  tickets,
  isLoading,
  onComplete,
  onReopen,
  onEdit,
  onDelete,
}: TicketListProps) {
  if (isLoading) {
    return <TicketListSkeleton />;
  }

  if (tickets.length === 0) {
    return (
      <Card className="p-12 text-center">
        <p className="text-muted-foreground">暂无 Ticket</p>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {tickets.map((ticket) => (
        <TicketCard
          key={ticket.id}
          ticket={ticket}
          onComplete={onComplete}
          onReopen={onReopen}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}
