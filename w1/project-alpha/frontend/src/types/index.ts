// Type definitions

export interface Tag {
  id: string;
  name: string;
  color: string;
  ticketCount?: number;
  createdAt: string;
  updatedAt: string;
}

export interface Ticket {
  id: string;
  title: string;
  description: string | null;
  status: "open" | "completed";
  completedAt: string | null;
  tags: Tag[];
  createdAt: string;
  updatedAt: string;
}

export interface CreateTicketInput {
  title: string;
  description?: string;
  tagIds: string[];
}

export interface UpdateTicketInput {
  title: string;
  description?: string;
  tagIds: string[];
}

export interface CreateTagInput {
  name: string;
  color: string;
}

export interface UpdateTagInput {
  name: string;
  color: string;
}

export interface TicketFilters {
  tagIds?: string[];
  status?: "open" | "completed";
  search?: string;
  sortBy?: "created_at" | "updated_at" | "completed_at" | "title";
  sortOrder?: "asc" | "desc";
  page?: number;
  pageSize?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}

export interface SuccessResponse {
  success: boolean;
}

export interface ErrorDetail {
  code: string;
  message: string;
}

export interface ErrorResponse {
  detail: ErrorDetail;
}
