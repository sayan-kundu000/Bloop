import { useQuery } from '@tanstack/react-query';
import { ttsFeatureApi } from '../api/tts.api';
import { Voice } from '../../../types';

export function useVoices(languageCode?: string | null) {
  const query = useQuery<Voice[], Error>({
    queryKey: ['voices', { language: languageCode || 'all' }],
    queryFn: () =>
      ttsFeatureApi.getVoices(
        languageCode ? { language_code: languageCode } : undefined
      ),
    staleTime: 1000 * 60 * 5, // 5 minutes cache
    refetchOnWindowFocus: false,
  });

  return {
    voices: query.data || [],
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    refetch: query.refetch,
  };
}
