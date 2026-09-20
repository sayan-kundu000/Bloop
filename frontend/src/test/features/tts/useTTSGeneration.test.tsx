import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useTTSGeneration } from '../../../features/tts/hooks/useTTSGeneration';
import { ttsFeatureApi } from '../../../features/tts/api/tts.api';
import { TTSGenerationPayload } from '../../../features/tts/types/tts.types';
import { TTSResponse } from '../../../types';
import { FrontendApiError } from '../../../lib/api/errors';

const mockResponse: TTSResponse = {
  generation_id: 42,
  audio_url: '/api/v1/tts/audio/gen_42.mp3',
  download_url: '/api/v1/tts/download/gen_42.mp3',
  text: 'Hello world from test',
  char_count: 21,
  word_count: 4,
  language: 'en-US',
  voice_id: 'voice-dyn-01',
  voice_name: 'Dynamic Voice',
  duration_seconds: 1.8,
  provider: 'dynamic-orchestrator',
  is_simulation: true,
  audio_format: 'mp3',
  content_type: 'audio/mpeg',
};

const mockPayload: TTSGenerationPayload = {
  text: 'Hello world from test',
  language: 'en-US',
  voice_id: 'voice-dyn-01',
  speed: 1.0,
  pitch: 1.0,
  emotion: 'Neutral',
};

function createWrapper(queryClient: QueryClient) {
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}

describe('useTTSGeneration Hook', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    vi.clearAllMocks();
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });
  });

  it('initializes in idle state', () => {
    const { result } = renderHook(() => useTTSGeneration(), {
      wrapper: createWrapper(queryClient),
    });

    expect(result.current.isPending).toBe(false);
    expect(result.current.isSuccess).toBe(false);
    expect(result.current.isError).toBe(false);
    expect(result.current.data).toBeNull();
    expect(result.current.error).toBeNull();
    expect(result.current.friendlyError).toBeNull();
  });

  it('successfully synthesizes speech and invalidates history query cache', async () => {
    vi.spyOn(ttsFeatureApi, 'generateSpeech').mockResolvedValue(mockResponse);
    const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');
    const onSuccessMock = vi.fn();

    const { result } = renderHook(() => useTTSGeneration({ onSuccess: onSuccessMock }), {
      wrapper: createWrapper(queryClient),
    });

    act(() => {
      result.current.mutate(mockPayload);
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.isPending).toBe(false);
    expect(result.current.data).toEqual(mockResponse);
    expect(result.current.error).toBeNull();
    expect(onSuccessMock).toHaveBeenCalledWith(mockResponse);
    expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['history'] });
  });

  it('prevents duplicate concurrent submissions when isPending is true', async () => {
    let resolvePromise: (res: TTSResponse) => void;
    const pendingPromise = new Promise<TTSResponse>((resolve) => {
      resolvePromise = resolve;
    });

    const generateSpy = vi.spyOn(ttsFeatureApi, 'generateSpeech').mockReturnValue(pendingPromise);

    const { result } = renderHook(() => useTTSGeneration(), {
      wrapper: createWrapper(queryClient),
    });

    act(() => {
      result.current.mutate(mockPayload);
    });

    await waitFor(() => {
      expect(result.current.isPending).toBe(true);
      expect(generateSpy).toHaveBeenCalledTimes(1);
    });

    // Attempt second submission while still pending (double-click simulation)
    act(() => {
      result.current.mutate(mockPayload);
    });

    // Still only 1 invocation permitted
    expect(generateSpy).toHaveBeenCalledTimes(1);

    // Resolve original promise
    await act(async () => {
      resolvePromise!(mockResponse);
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });
  });

  it('handles backend error codes with normalized friendly error messages', async () => {
    const apiError = new FrontendApiError(
      'Selected voice does not match language',
      'VOICE_LANGUAGE_MISMATCH',
      400
    );
    vi.spyOn(ttsFeatureApi, 'generateSpeech').mockRejectedValue(apiError);
    const onErrorMock = vi.fn();

    const { result } = renderHook(() => useTTSGeneration({ onError: onErrorMock }), {
      wrapper: createWrapper(queryClient),
    });

    act(() => {
      result.current.mutate(mockPayload);
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.isPending).toBe(false);
    expect(result.current.friendlyError).toBe(
      'The selected voice is not available for this language.'
    );
    expect(onErrorMock).toHaveBeenCalled();
  });

  it('identifies retryable errors and allows re-dispatching with retry()', async () => {
    const timeoutError = new FrontendApiError(
      'Provider timeout',
      'PROVIDER_TIMEOUT',
      504
    );
    const generateSpy = vi
      .spyOn(ttsFeatureApi, 'generateSpeech')
      .mockRejectedValueOnce(timeoutError)
      .mockResolvedValueOnce(mockResponse);

    const { result } = renderHook(() => useTTSGeneration(), {
      wrapper: createWrapper(queryClient),
    });

    act(() => {
      result.current.mutate(mockPayload);
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.isRetryable).toBe(true);
    expect(result.current.friendlyError).toBe('Speech generation took too long. Please try again.');

    // User triggers retry
    act(() => {
      result.current.retry();
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(generateSpy).toHaveBeenCalledTimes(2);
    expect(result.current.data).toEqual(mockResponse);
  });

  it('resets state when reset() is invoked', async () => {
    vi.spyOn(ttsFeatureApi, 'generateSpeech').mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useTTSGeneration(), {
      wrapper: createWrapper(queryClient),
    });

    act(() => {
      result.current.mutate(mockPayload);
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    act(() => {
      result.current.reset();
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(false);
      expect(result.current.data).toBeNull();
    });
  });

  describe('HTTP & Domain Error Categories (Requirement 67)', () => {
    it.each([
      {
        status: 401,
        code: 'AUTHENTICATION_REQUIRED',
        expected: 'Session expired. Please sign in again.',
        retryable: false,
      },
      {
        status: 403,
        code: 'FORBIDDEN',
        expected: 'You do not have permission to synthesize speech.',
        retryable: false,
      },
      {
        status: 429,
        code: 'RATE_LIMIT_EXCEEDED',
        expected: 'Too many requests. Please wait a moment before trying again.',
        retryable: false,
      },
      {
        status: 503,
        code: 'SERVICE_UNAVAILABLE',
        expected: 'Speech generation service is temporarily unavailable.',
        retryable: true,
      },
      {
        status: 502,
        code: 'PROVIDER_ERROR',
        expected: 'Voice provider encountered an issue. Please try again.',
        retryable: true,
      },
      {
        status: 0,
        code: 'NETWORK_ERROR',
        expected: "We couldn't reach Bloop. Check your connection and try again.",
        retryable: true,
      },
    ])(
      'maps error $code ($status) to "$expected" (retryable: $retryable)',
      async ({ status, code, expected, retryable }) => {
        const error = new FrontendApiError(expected, code, status);
        vi.spyOn(ttsFeatureApi, 'generateSpeech').mockRejectedValue(error);

        const { result } = renderHook(() => useTTSGeneration(), {
          wrapper: createWrapper(queryClient),
        });

        act(() => {
          result.current.mutate(mockPayload);
        });

        await waitFor(() => {
          expect(result.current.isError).toBe(true);
        });

        expect(result.current.friendlyError).toBe(expected);
        expect(result.current.isRetryable).toBe(retryable);
      }
    );
  });
});
