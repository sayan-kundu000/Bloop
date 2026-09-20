import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { historyApi } from '../../../api/client';
import { Favorite, PaginatedResponse } from '../../../types';

export interface FavoritesFilterParams {
  search?: string;
  language?: string;
  page?: number;
  page_size?: number;
}

/**
 * TanStack Query hook to retrieve the authenticated user's starred favorites.
 */
export function useFavorites(
  params?: FavoritesFilterParams
): UseQueryResult<PaginatedResponse<Favorite>, Error> {
  return useQuery({
    queryKey: ['favorites', params],
    queryFn: () => historyApi.getFavorites(params),
    staleTime: 1000 * 30, // 30 seconds fresh
  });
}
