import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { TicketForm } from "@/components/tickets/TicketForm";
import { CreateTicketInput, UpdateTicketInput, Tag } from "@/types";

interface TicketFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  tags: Tag[];
  initialData?: CreateTicketInput | UpdateTicketInput;
  onSubmit: (data: CreateTicketInput | UpdateTicketInput) => void;
  onNewTag?: () => void;
  isLoading?: boolean;
  mode?: "create" | "edit";
}

export function TicketFormDialog({
  open,
  onOpenChange,
  tags,
  initialData,
  onSubmit,
  onNewTag,
  isLoading = false,
  mode = "create",
}: TicketFormDialogProps) {
  const handleSubmit = (data: CreateTicketInput | UpdateTicketInput) => {
    onSubmit(data);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {mode === "create" ? "新建 Ticket" : "编辑 Ticket"}
          </DialogTitle>
          <DialogDescription>
            {mode === "create"
              ? "创建一个新的 Ticket 来记录待办事项"
              : "修改 Ticket 信息"}
          </DialogDescription>
        </DialogHeader>
        <TicketForm
          tags={tags}
          initialData={initialData}
          onSubmit={handleSubmit}
          onCancel={() => onOpenChange(false)}
          onNewTag={onNewTag}
          isLoading={isLoading}
        />
      </DialogContent>
    </Dialog>
  );
}
