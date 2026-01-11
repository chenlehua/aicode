import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { tagApi } from "../lib/tagApi";
import { CreateTagInput, UpdateTagInput } from "../types";

/**
 * Query key factory for tags
 */
export const tagKeys = {
  all: ["tags"] as const,
  lists: () => [...tagKeys.all, "list"] as const,
  details: () => [...tagKeys.all, "detail"] as const,
  detail: (id: string) => [...tagKeys.details(), id] as const,
};

/**
 * Get all tags
 */
export function useTags() {
  return useQuery({
    queryKey: tagKeys.lists(),
    queryFn: () => tagApi.getTags(),
  });
}

/**
 * Get a single tag by ID
 */
export function useTag(id: string | undefined) {
  return useQuery({
    queryKey: tagKeys.detail(id!),
    queryFn: () => tagApi.getTag(id!),
    enabled: !!id,
  });
}

/**
 * Create tag mutation
 */
export function useCreateTag() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: CreateTagInput) => tagApi.createTag(input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: tagKeys.lists() });
    },
  });
}

/**
 * Update tag mutation
 */
export function useUpdateTag() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, input }: { id: string; input: UpdateTagInput }) =>
      tagApi.updateTag(id, input),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: tagKeys.lists() });
      queryClient.invalidateQueries({ queryKey: tagKeys.detail(data.id) });
    },
  });
}

/**
 * Delete tag mutation
 */
export function useDeleteTag() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => tagApi.deleteTag(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: tagKeys.lists() });
      // Also invalidate tickets since tag deletion affects ticket counts
      queryClient.invalidateQueries({ queryKey: ["tickets"] });
    },
  });
}
