/** API service configuration and base utilities. */

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.MODE === 'production' ? 'http://backend:8000' : 'http://localhost:8000');
const API_V1_PREFIX = '/api/v1';

export const API_BASE = `${API_BASE_URL}${API_V1_PREFIX}`;

/**
 * Fetch wrapper with error handling.
 */
export async function apiFetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      error: 'Unknown',
      message: `HTTP ${response.status}: ${response.statusText}`,
      status: response.status,
    }));
    error.status = response.status;
    throw error;
  }

  // Handle 204 No Content response (e.g., DELETE operations)
  if (response.status === 204) {
    return undefined as T;
  }

  // Check if response has content before parsing JSON
  const contentLength = response.headers.get('content-length');
  if (contentLength === '0') {
    return undefined as T;
  }

  return response.json();
}
