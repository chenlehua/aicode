import { useState } from "react";
import { MainLayout } from "@/components/layout/MainLayout";
import { TicketList } from "@/components/tickets/TicketList";
import { TicketFormDialog } from "@/components/dialogs/TicketFormDialog";
import { TagFormDialog } from "@/components/dialogs/TagFormDialog";
import { ConfirmDialog } from "@/components/dialogs/ConfirmDialog";
import { useTickets, useTags } from "@/hooks";
import {
  useCreateTicket,
  useUpdateTicket,
  useDeleteTicket,
  useCompleteTicket,
  useReopenTicket,
} from "@/hooks/useTickets";
import { useCreateTag, useUpdateTag, useDeleteTag } from "@/hooks/useTags";
import { useFilters } from "@/hooks/useFilters";
import { useToast } from "@/hooks/use-toast";
import {
  Ticket,
  Tag,
  CreateTicketInput,
  UpdateTicketInput,
  CreateTagInput,
  UpdateTagInput,
} from "@/types";
import { TicketStatus } from "@/components/filters/StatusFilter";

export function HomePage() {
  const { toast } = useToast();
  const { filters, setStatus, setTagIds, setSearch } = useFilters();

  // Queries
  const { data: ticketsData, isLoading: ticketsLoading } = useTickets(filters);
  const { data: tags = [] } = useTags();

  // Mutations
  const createTicket = useCreateTicket();
  const updateTicket = useUpdateTicket();
  const deleteTicket = useDeleteTicket();
  const completeTicket = useCompleteTicket();
  const reopenTicket = useReopenTicket();
  const createTag = useCreateTag();
  const updateTag = useUpdateTag();
  const deleteTag = useDeleteTag();

  // Dialog states
  const [ticketDialogOpen, setTicketDialogOpen] = useState(false);
  const [tagDialogOpen, setTagDialogOpen] = useState(false);
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [editingTicket, setEditingTicket] = useState<Ticket | null>(null);
  const [editingTag, setEditingTag] = useState<Tag | null>(null);
  const [deletingTicket, setDeletingTicket] = useState<string | null>(null);
  const [deletingTag, setDeletingTag] = useState<string | null>(null);

  // Ticket handlers
  const handleNewTicket = () => {
    setEditingTicket(null);
    setTicketDialogOpen(true);
  };

  const handleEditTicket = (ticketId: string) => {
    const ticket = ticketsData?.items.find((t) => t.id === ticketId);
    if (ticket) {
      setEditingTicket(ticket);
      setTicketDialogOpen(true);
    }
  };

  const handleDeleteTicket = (ticketId: string) => {
    setDeletingTicket(ticketId);
    setConfirmDialogOpen(true);
  };

  const handleConfirmDeleteTicket = async () => {
    if (!deletingTicket) return;
    try {
      await deleteTicket.mutateAsync(deletingTicket);
      toast({
        title: "成功",
        description: "Ticket 已删除",
      });
    } catch (error) {
      toast({
        title: "错误",
        description: "删除失败",
        variant: "destructive",
      });
    } finally {
      setDeletingTicket(null);
    }
  };

  const handleTicketSubmit = async (
    data: CreateTicketInput | UpdateTicketInput,
  ) => {
    try {
      if (editingTicket) {
        await updateTicket.mutateAsync({ id: editingTicket.id, input: data });
        toast({
          title: "成功",
          description: "Ticket 已更新",
        });
      } else {
        await createTicket.mutateAsync(data);
        toast({
          title: "成功",
          description: "Ticket 已创建",
        });
      }
      setTicketDialogOpen(false);
      setEditingTicket(null);
    } catch (error) {
      toast({
        title: "错误",
        description: editingTicket ? "更新失败" : "创建失败",
        variant: "destructive",
      });
    }
  };

  const handleCompleteTicket = async (ticketId: string) => {
    try {
      await completeTicket.mutateAsync(ticketId);
      toast({
        title: "成功",
        description: "Ticket 已完成",
      });
    } catch (error) {
      toast({
        title: "错误",
        description: "操作失败",
        variant: "destructive",
      });
    }
  };

  const handleReopenTicket = async (ticketId: string) => {
    try {
      await reopenTicket.mutateAsync(ticketId);
      toast({
        title: "成功",
        description: "Ticket 已重新打开",
      });
    } catch (error) {
      toast({
        title: "错误",
        description: "操作失败",
        variant: "destructive",
      });
    }
  };

  // Tag handlers
  const handleNewTag = () => {
    setEditingTag(null);
    setTagDialogOpen(true);
  };

  const handleConfirmDeleteTag = async () => {
    if (!deletingTag) return;
    try {
      await deleteTag.mutateAsync(deletingTag);
      toast({
        title: "成功",
        description: "标签已删除",
      });
    } catch (error) {
      toast({
        title: "错误",
        description: "删除失败",
        variant: "destructive",
      });
    } finally {
      setDeletingTag(null);
    }
  };

  const handleTagSubmit = async (data: CreateTagInput | UpdateTagInput) => {
    try {
      if (editingTag) {
        await updateTag.mutateAsync({ id: editingTag.id, input: data });
        toast({
          title: "成功",
          description: "标签已更新",
        });
      } else {
        await createTag.mutateAsync(data);
        toast({
          title: "成功",
          description: "标签已创建",
        });
      }
      setTagDialogOpen(false);
      setEditingTag(null);
    } catch (error) {
      toast({
        title: "错误",
        description: editingTag ? "更新失败" : "创建失败",
        variant: "destructive",
      });
    }
  };

  // Convert status filter
  const statusFilter: TicketStatus =
    filters.status === "open"
      ? "open"
      : filters.status === "completed"
        ? "completed"
        : "all";

  return (
    <>
      <MainLayout
        search={filters.search || ""}
        onSearchChange={setSearch}
        status={statusFilter}
        onStatusChange={(status) =>
          setStatus(status === "all" ? undefined : status)
        }
        tags={tags}
        selectedTagIds={filters.tagIds || []}
        onTagIdsChange={setTagIds}
        onNewTicket={handleNewTicket}
        onNewTag={handleNewTag}
      >
        <TicketList
          tickets={ticketsData?.items || []}
          isLoading={ticketsLoading}
          onComplete={handleCompleteTicket}
          onReopen={handleReopenTicket}
          onEdit={handleEditTicket}
          onDelete={handleDeleteTicket}
        />
      </MainLayout>

      {/* Dialogs */}
      <TicketFormDialog
        open={ticketDialogOpen}
        onOpenChange={setTicketDialogOpen}
        tags={tags}
        initialData={
          editingTicket
            ? {
                title: editingTicket.title,
                description: editingTicket.description || undefined,
                tagIds: editingTicket.tags.map((t) => t.id),
              }
            : undefined
        }
        onSubmit={handleTicketSubmit}
        onNewTag={handleNewTag}
        isLoading={createTicket.isPending || updateTicket.isPending}
        mode={editingTicket ? "edit" : "create"}
      />

      <TagFormDialog
        open={tagDialogOpen}
        onOpenChange={setTagDialogOpen}
        initialData={
          editingTag
            ? {
                name: editingTag.name,
                color: editingTag.color,
              }
            : undefined
        }
        onSubmit={handleTagSubmit}
        isLoading={createTag.isPending || updateTag.isPending}
        mode={editingTag ? "edit" : "create"}
      />

      <ConfirmDialog
        open={confirmDialogOpen}
        onOpenChange={setConfirmDialogOpen}
        title={deletingTicket ? "删除 Ticket" : "删除标签"}
        description={
          deletingTicket
            ? "确定要删除这个 Ticket 吗？此操作无法撤销。"
            : "确定要删除这个标签吗？所有关联的 Ticket 将自动解除关联。"
        }
        confirmText="删除"
        onConfirm={
          deletingTicket ? handleConfirmDeleteTicket : handleConfirmDeleteTag
        }
        variant="destructive"
      />
    </>
  );
}
