import { Ticket } from "@/types";
import { Card } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { TagBadge } from "@/components/tags/TagBadge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { MoreVertical, Edit, Trash2 } from "lucide-react";
import { cn, formatDate } from "@/lib/utils";

interface TicketCardProps {
  ticket: Ticket;
  onComplete: (id: string) => void;
  onReopen: (id: string) => void;
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
}

export function TicketCard({
  ticket,
  onComplete,
  onReopen,
  onEdit,
  onDelete,
}: TicketCardProps) {
  const isCompleted = ticket.status === "completed";

  const handleToggleStatus = () => {
    if (isCompleted) {
      onReopen(ticket.id);
    } else {
      onComplete(ticket.id);
    }
  };

  return (
    <Card
      className={cn(
        "p-4 hover:shadow-md transition-shadow",
        isCompleted && "opacity-60",
      )}
    >
      <div className="flex items-start gap-3">
        <Checkbox
          checked={isCompleted}
          onCheckedChange={handleToggleStatus}
          className="mt-1"
        />
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <h3
              className={cn(
                "font-semibold text-base md:text-lg break-words",
                isCompleted && "line-through text-muted-foreground",
              )}
            >
              {ticket.title}
            </h3>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem
                  onClick={() => onEdit(ticket.id)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      onEdit(ticket.id);
                    }
                  }}
                >
                  <Edit className="mr-2 h-4 w-4" />
                  编辑
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={() => onDelete(ticket.id)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      onDelete(ticket.id);
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
                "text-sm text-muted-foreground mt-2 line-clamp-2",
                isCompleted && "line-through",
              )}
            >
              {ticket.description}
            </p>
          )}
          <div className="flex items-center gap-2 mt-3 flex-wrap">
            {ticket.tags.map((tag) => (
              <TagBadge key={tag.id} tag={tag} />
            ))}
          </div>
          <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 mt-3 text-xs text-muted-foreground">
            <span>创建于 {formatDate(ticket.createdAt)}</span>
            {ticket.completedAt && (
              <span>完成于 {formatDate(ticket.completedAt)}</span>
            )}
          </div>
        </div>
      </div>
    </Card>
  );
}
