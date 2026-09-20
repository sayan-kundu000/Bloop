import { useState, useCallback, useRef } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { ttsFeatureApi } from '../api/tts.api';
import { TTSGenerationPayload, TTSGenerationOptions } from '../types/tts.types';
import { TTSResponse } from '../../../types';
import { FrontendApiError, normalizeApiError } from '../../../lib/api/errors';
import { getFriendlyTTSErrorMessage, isRetryableTTSError } from '../utils/ttsErrorMapping';

/**
 * TanStack Query Mutation hook managing the speech generation lifecycle.
 * Features:
 * - Duplicate request prevention (no-op while mutation is pending).
 * - Automatic query cache invalidation for user speech history (`['history']`).
 * - Safe error normalization to FrontendApiError and friendly UX error resolution.
 * - Retry capability that can re-dispatch the last submitted payload or a new validated payload.
 * - Clean handoff of generated TTSResponse to the audio player layer.
 */
export function useTTSGeneration(options?: TTSGenerationOptions) {
  const queryClient = useQueryClient();
  const [lastPayload, setLastPayload] = useState<TTSGenerationPayload | null>(null);

  // Keep latest callbacks in ref to avoid stale closures during async transitions
  const optionsRef = useRef(options);
  optionsRef.current = options;

  const mutation = useMutation<TTSResponse, FrontendApiError, TTSGenerationPayload>({
    mutationFn: async (payload: TTSGenerationPayload) => {
      return await ttsFeatureApi.generateSpeech(payload);
    },
    onSuccess: (data) => {
      // Invalidate speech history so newly generated audio appears in history/favorites
      queryClient.invalidateQueries({ queryKey: ['history'] });

      if (optionsRef.current?.onSuccess) {
        optionsRef.current.onSuccess(data);
      }
    },
    onError: (err: unknown) => {
      const normalized = err instanceof FrontendApiError ? err : normalizeApiError(err);
      if (optionsRef.current?.onError) {
        optionsRef.current.onError(normalized);
      }
    },
  });

  const isPending = mutation.isPending;
  const isSuccess = mutation.isSuccess;
  const isError = mutation.isError;
  const data = mutation.data ?? null;
  const rawError = mutation.error ?? null;
  const normalizedError = rawError
    ? rawError instanceof FrontendApiError
      ? rawError
      : normalizeApiError(rawError)
    : null;

  const friendlyError = normalizedError ? getFriendlyTTSErrorMessage(normalizedError) : null;
  const isRetryable = normalizedError ? isRetryableTTSError(normalizedError) : false;

  /**
   * Dispatches speech synthesis mutation with duplicate submission protection.
   */
  const generate = useCallback(
    (payload: TTSGenerationPayload) => {
      // Enforce duplicate request prevention
      if (isPending) {
        return;
      }
      setLastPayload(payload);
      mutation.mutate(payload);
    },
    [isPending, mutation]
  );

  /**
   * Async variant returning Promise<TTSResponse>
   */
  const generateAsync = useCallback(
    async (payload: TTSGenerationPayload): Promise<TTSResponse> => {
      if (isPending) {
        throw new FrontendApiError(
          'A speech generation request is already in progress.',
          'CONCURRENT_GENERATION_PREVENTED'
        );
      }
      setLastPayload(payload);
      return await mutation.mutateAsync(payload);
    },
    [isPending, mutation]
  );

  /**
   * Retries synthesis with the current/last submitted payload
   */
  const retry = useCallback(
    (overridePayload?: TTSGenerationPayload) => {
      const targetPayload = overridePayload || lastPayload;
      if (!targetPayload || isPending) {
        return;
      }
      mutation.mutate(targetPayload);
    },
    [lastPayload, isPending, mutation]
  );

  const reset = useCallback(() => {
    mutation.reset();
  }, [mutation]);

  return {
    mutate: generate,
    mutateAsync: generateAsync,
    isPending,
    isSuccess,
    isError,
    data,
    error: normalizedError,
    friendlyError,
    isRetryable,
    reset,
    retry,
    lastPayload,
  };
}
