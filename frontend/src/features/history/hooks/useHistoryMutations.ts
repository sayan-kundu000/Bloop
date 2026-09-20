import { useMutation, useQueryClient, UseMutationResult } from '@tanstack/react-query';
import { historyApi } from '../../../api/client';
import { SpeechGeneration } from '../../../types';

export function useToggleFavoriteMutation(): UseMutationResult<void, Error, SpeechGeneration> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (gen: SpeechGeneration) => {
      if (gen.is_favorite) {
        if (gen.favorite_id) {
          await historyApi.removeFavorite(gen.favorite_id);
        } else {
          await historyApi.removeFavoriteByGeneration(gen.id);
        }
      } else {
        await historyApi.addFavorite(gen.id);
      }
    },
    onSuccess: () => {
      // Invalidate both history and favorites queries to maintain strict cache consistency
      queryClient.invalidateQueries({ queryKey: ['history'] });
      queryClient.invalidateQueries({ queryKey: ['favorites'] });
      queryClient.invalidateQueries({ queryKey: ['generation-detail'] });
      queryClient.invalidateQueries({ queryKey: ['history_count'] });
      queryClient.invalidateQueries({ queryKey: ['favorites_count'] });
    },
  });
}

export function useDeleteGenerationMutation(): UseMutationResult<void, Error, number> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      await historyApi.deleteGeneration(id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['history'] });
      queryClient.invalidateQueries({ queryKey: ['favorites'] });
      queryClient.invalidateQueries({ queryKey: ['history_count'] });
      queryClient.invalidateQueries({ queryKey: ['favorites_count'] });
    },
  });
}
