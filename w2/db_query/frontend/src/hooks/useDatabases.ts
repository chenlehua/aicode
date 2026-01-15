/** Custom hooks for database operations. */

import { useState, useEffect } from 'react';
import { apiFetch } from '../services/api';
import type { Database, DatabaseWithMetadata } from '../types';

/**
 * Hook to list all databases.
 */
export function useDatabases() {
  const [data, setData] = useState<Database[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isError, setIsError] = useState(false);

  const fetchDatabases = async () => {
    try {
      setIsLoading(true);
      setIsError(false);
      const result = await apiFetch<Database[]>('/dbs');
      setData(result);
    } catch (error) {
      setIsError(true);
      console.error('Failed to fetch databases:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDatabases();
  }, []);

  return { data, isLoading, isError, refetch: fetchDatabases };
}

/**
 * Hook to get a single database with metadata.
 */
export function useDatabase(name: string) {
  const [data, setData] = useState<DatabaseWithMetadata | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isError, setIsError] = useState(false);

  useEffect(() => {
    if (!name) {
      setIsLoading(false);
      return;
    }

    let cancelled = false;

    async function fetchDatabase() {
      try {
        setIsLoading(true);
        setIsError(false);
        const result = await apiFetch<DatabaseWithMetadata>(`/dbs/${name}`);
        if (!cancelled) {
          setData(result);
        }
      } catch (error) {
        if (!cancelled) {
          setIsError(true);
          console.error('Failed to fetch database:', error);
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    fetchDatabase();

    return () => {
      cancelled = true;
    };
  }, [name]);

  return { data, isLoading, isError };
}
