import { useState, useCallback } from "react";
import { TicketFilters } from "../types";

const DEFAULT_FILTERS: TicketFilters = {
  status: undefined,
  tagIds: [],
  search: "",
  sortBy: "created_at",
  sortOrder: "desc",
  page: 1,
  pageSize: 20,
};

/**
 * Hook to manage ticket filters
 */
export function useFilters() {
  const [filters, setFilters] = useState<TicketFilters>(DEFAULT_FILTERS);

  const updateFilter = useCallback(
    <K extends keyof TicketFilters>(key: K, value: TicketFilters[K]) => {
      setFilters((prev) => ({
        ...prev,
        [key]: value,
        // Reset page when filters change (except when updating page itself)
        page: key === "page" ? (value as number) : 1,
      }));
    },
    [],
  );

  const setStatus = useCallback(
    (status: "open" | "completed" | undefined) => {
      updateFilter("status", status);
    },
    [updateFilter],
  );

  const setTagIds = useCallback(
    (tagIds: string[]) => {
      updateFilter("tagIds", tagIds);
    },
    [updateFilter],
  );

  const setSearch = useCallback(
    (search: string) => {
      updateFilter("search", search);
    },
    [updateFilter],
  );

  const setSortBy = useCallback(
    (sortBy: "created_at" | "updated_at" | "completed_at" | "title") => {
      updateFilter("sortBy", sortBy);
    },
    [updateFilter],
  );

  const setSortOrder = useCallback(
    (sortOrder: "asc" | "desc") => {
      updateFilter("sortOrder", sortOrder);
    },
    [updateFilter],
  );

  const setPage = useCallback(
    (page: number) => {
      updateFilter("page", page);
    },
    [updateFilter],
  );

  const setPageSize = useCallback(
    (pageSize: number) => {
      updateFilter("pageSize", pageSize);
    },
    [updateFilter],
  );

  const resetFilters = useCallback(() => {
    setFilters(DEFAULT_FILTERS);
  }, []);

  return {
    filters,
    setStatus,
    setTagIds,
    setSearch,
    setSortBy,
    setSortOrder,
    setPage,
    setPageSize,
    resetFilters,
    updateFilter,
  };
}
