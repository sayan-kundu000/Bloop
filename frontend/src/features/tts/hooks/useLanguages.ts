import { useQuery } from '@tanstack/react-query';
import { ttsFeatureApi } from '../api/tts.api';
import { Language } from '../../../types';

export function useLanguages() {
  const query = useQuery<Language[], Error>({
    queryKey: ['languages'],
    queryFn: ttsFeatureApi.getLanguages,
    staleTime: 1000 * 60 * 5, // 5 minutes cache
    refetchOnWindowFocus: false,
  });

  return {
    languages: query.data || [],
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    refetch: query.refetch,
  };
}
