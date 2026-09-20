import { useMutation, useQueryClient, UseMutationResult } from '@tanstack/react-query';
import { historyApi } from '../../../api/client';
import { Favorite } from '../../../types';

export function useAddFavoriteMutation(): UseMutationResult<Favorite, Error, { generationId: number; label?: string }> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ generationId, label }) => historyApi.addFavorite(generationId, label),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['favorites'] });
      queryClient.invalidateQueries({ queryKey: ['history'] });
      queryClient.invalidateQueries({ queryKey: ['generation-detail'] });
      queryClient.invalidateQueries({ queryKey: ['history_count'] });
      queryClient.invalidateQueries({ queryKey: ['favorites_count'] });
    },
  });
}

export function useRemoveFavoriteMutation(): UseMutationResult<void, Error, number> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (favoriteId: number) => historyApi.removeFavorite(favoriteId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['favorites'] });
      queryClient.invalidateQueries({ queryKey: ['history'] });
      queryClient.invalidateQueries({ queryKey: ['generation-detail'] });
      queryClient.invalidateQueries({ queryKey: ['history_count'] });
      queryClient.invalidateQueries({ queryKey: ['favorites_count'] });
    },
  });
}
