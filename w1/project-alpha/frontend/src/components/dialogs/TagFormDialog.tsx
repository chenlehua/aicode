import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { TagForm } from "@/components/tags/TagForm";
import { CreateTagInput, UpdateTagInput } from "@/types";

interface TagFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  initialData?: CreateTagInput | UpdateTagInput;
  onSubmit: (data: CreateTagInput | UpdateTagInput) => void;
  isLoading?: boolean;
  mode?: "create" | "edit";
}

export function TagFormDialog({
  open,
  onOpenChange,
  initialData,
  onSubmit,
  isLoading = false,
  mode = "create",
}: TagFormDialogProps) {
  const handleSubmit = (data: CreateTagInput | UpdateTagInput) => {
    onSubmit(data);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            {mode === "create" ? "新建标签" : "编辑标签"}
          </DialogTitle>
          <DialogDescription>
            {mode === "create"
              ? "创建一个新标签用于分类 Ticket"
              : "修改标签信息"}
          </DialogDescription>
        </DialogHeader>
        <TagForm
          initialData={initialData}
          onSubmit={handleSubmit}
          onCancel={() => onOpenChange(false)}
          isLoading={isLoading}
        />
      </DialogContent>
    </Dialog>
  );
}
