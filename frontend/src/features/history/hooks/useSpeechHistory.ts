import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { historyApi } from '../../../api/client';
import { PaginatedResponse, SpeechGeneration } from '../../../types';

export interface SpeechHistoryFilterParams {
  search?: string;
  language?: string;
  status?: string;
  favorite?: boolean;
  created_after?: string;
  created_before?: string;
  sort_by?: string;
  order?: string;
  page?: number;
  page_size?: number;
}

/**
 * TanStack Query hook to retrieve paginated, searchable, and filterable speech generation history.
 * Strictly scoped to the authenticated user's records on the server.
 */
export function useSpeechHistory(
  params?: SpeechHistoryFilterParams
): UseQueryResult<PaginatedResponse<SpeechGeneration>, Error> {
  return useQuery({
    queryKey: ['history', params],
    queryFn: () => historyApi.getHistory(params),
    staleTime: 1000 * 30, // 30 seconds fresh
  });
}

/**
 * TanStack Query hook to retrieve a single speech generation record by ID with ownership validation.
 */
export function useSpeechGeneration(
  id: number,
  enabled = true
): UseQueryResult<SpeechGeneration, Error> {
  return useQuery({
    queryKey: ['generation-detail', id],
    queryFn: () => historyApi.getGeneration(id),
    enabled: enabled && !isNaN(id) && id > 0,
    staleTime: 1000 * 60 * 2, // 2 minutes fresh
  });
}
