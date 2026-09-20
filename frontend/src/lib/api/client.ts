/**
 * Centralized Typed API Client (Fetch Alternative)
 * Handles HTTP requests, JSON serialization, headers, and normalized error throwing.
 */

import { FrontendApiError, normalizeApiError } from './errors';

export { FrontendApiError, normalizeApiError };

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = localStorage.getItem('bloop_token') || localStorage.getItem('bloop_auth_token');
  const headers = new Headers(options.headers || {});
  
  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }
  
  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  let response: Response;
  try {
    response = await fetch(endpoint, {
      ...options,
      headers,
    });
  } catch (netErr) {
    throw normalizeApiError(netErr);
  }

  if (!response.ok) {
    let errorData: any = {};
    try {
      const json = await response.json();
      errorData = json.error || json;
    } catch {
      errorData = { message: response.statusText };
    }

    if (response.status === 401) {
      if (typeof window !== 'undefined' && localStorage.getItem('bloop_token')) {
        localStorage.removeItem('bloop_token');
      }
    }

    throw new FrontendApiError(
      errorData.message || 'Request failed',
      errorData.code || `HTTP_${response.status}`,
      response.status,
      errorData.details
    );
  }

  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    const json = await response.json();
    return (json.data !== undefined ? json.data : json) as T;
  }

  return (await response.blob()) as unknown as T;
}
