/** Custom hooks for natural language query operations. */

import { useState } from 'react';
import { apiFetch } from '../services/api';
import type { GeneratedSQL, NaturalQueryRequest } from '../types';

interface UseNaturalQueryOptions {
  onSuccess?: (result: GeneratedSQL) => void;
  onError?: (error: Error) => void;
}

export function useNaturalQuery(databaseName: string, options?: UseNaturalQueryOptions) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<GeneratedSQL | null>(null);
  const [error, setError] = useState<string | null>(null);

  const generateSQL = async (prompt: string) => {
    if (!prompt.trim()) {
      setError('Prompt cannot be empty');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await apiFetch<GeneratedSQL>(`/dbs/${databaseName}/query/natural`, {
        method: 'POST',
        body: JSON.stringify({ prompt } as NaturalQueryRequest),
      });
      setResult(response);
      options?.onSuccess?.(response);
    } catch (err: unknown) {
      const error = err instanceof Error ? err : new Error('Failed to generate SQL');
      const errorMessage = (err as { message?: string })?.message || error.message;
      setError(errorMessage);
      options?.onError?.(error);
    } finally {
      setLoading(false);
    }
  };

  return {
    generateSQL,
    loading,
    result,
    error,
  };
}
