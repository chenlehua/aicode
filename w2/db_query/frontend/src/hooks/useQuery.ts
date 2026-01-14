/** Custom hooks for query operations. */

import { useState } from 'react';
import { apiFetch } from '../services/api';
import type { QueryRequest, QueryResult } from '../types';

interface UseQueryOptions {
  onSuccess?: (result: QueryResult) => void;
  onError?: (error: Error) => void;
}

export function useQuery(databaseName: string, options?: UseQueryOptions) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<QueryResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const executeQuery = async (sql: string) => {
    if (!sql.trim()) {
      setError('SQL query cannot be empty');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await apiFetch<QueryResult>(`/dbs/${databaseName}/query`, {
        method: 'POST',
        body: JSON.stringify({ sql } as QueryRequest),
      });
      setResult(response);
      options?.onSuccess?.(response);
    } catch (err: unknown) {
      const error = err instanceof Error ? err : new Error('Failed to execute query');
      const errorMessage = (err as { message?: string })?.message || error.message;
      setError(errorMessage);
      options?.onError?.(error);
    } finally {
      setLoading(false);
    }
  };

  return {
    executeQuery,
    loading,
    result,
    error,
  };
}
