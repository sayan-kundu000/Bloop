import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { TextWorkspace } from '../../../features/tts/components/TextWorkspace';
import { useWorkspaceStore } from '../../../stores/workspaceStore';
import { ttsFeatureApi } from '../../../features/tts/api/tts.api';
import { Language, Voice } from '../../../types';

// Mock languages and dynamic voices without real ElevenLabs voice IDs
const mockLanguages: Language[] = [
  { code: 'en-US', name: 'English (US)', is_active: true },
  { code: 'es-ES', name: 'Spanish (Spain)', is_active: true },
];

const mockVoices: Voice[] = [
  {
    id: 1,
    voice_id: 'voice-dyn-en',
    name: 'Dynamic English Voice',
    language_code: 'en-US',
    supported_languages: ['en-US'],
    gender: 'female',
    provider: 'dynamic',
    is_active: true,
    is_user_configured: false,
  },
  {
    id: 2,
    voice_id: 'voice-dyn-es',
    name: 'Dynamic Spanish Voice',
    language_code: 'es-ES',
    supported_languages: ['es-ES'],
    gender: 'male',
    provider: 'dynamic',
    is_active: true,
    is_user_configured: false,
  },
];

function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
    },
  });
}

describe('TextWorkspace Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(ttsFeatureApi, 'getLanguages').mockResolvedValue(mockLanguages);
    vi.spyOn(ttsFeatureApi, 'getVoices').mockImplementation(async (params) => {
      if (params?.language_code === 'es-ES') {
        return [mockVoices[1]];
      }
      if (params?.language_code === 'en-US') {
        return [mockVoices[0]];
      }
      return mockVoices;
    });

    useWorkspaceStore.setState({
      text: 'Initial test text for synthesis.',
      languageCode: 'en-US',
      voiceId: 'voice-dyn-en',
      speed: 1.0,
      pitch: 1.0,
      emotion: 'Neutral',
    });
  });

  it('renders text editor, metrics bar, and language/voice selectors', async () => {
    const queryClient = createTestQueryClient();
    render(
      <QueryClientProvider client={queryClient}>
        <TextWorkspace />
      </QueryClientProvider>
    );

    expect(screen.getByLabelText(/speech text/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /generate speech/i })).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByLabelText(/speech language/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/speech voice/i)).toBeInTheDocument();
      expect(screen.getByText(/characters:/i)).toBeInTheDocument();
      expect(screen.getByText(/words:/i)).toBeInTheDocument();
    });
  });

  it('updates text metrics live when typing in the editor', async () => {
    const queryClient = createTestQueryClient();
    render(
      <QueryClientProvider client={queryClient}>
        <TextWorkspace />
      </QueryClientProvider>
    );

    const textarea = screen.getByLabelText(/speech text/i);
    fireEvent.change(textarea, { target: { value: 'One two three four' } });

    await waitFor(() => {
      expect(useWorkspaceStore.getState().text).toBe('One two three four');
      expect(screen.getByText('18')).toBeInTheDocument(); // character count
      expect(screen.getByText('4')).toBeInTheDocument(); // word count
    });
  });

  it('clears text and resets metrics when Clear is clicked', async () => {
    // Set short text so confirmation modal is skipped
    useWorkspaceStore.setState({ text: 'Short prompt' });

    const queryClient = createTestQueryClient();
    render(
      <QueryClientProvider client={queryClient}>
        <TextWorkspace />
      </QueryClientProvider>
    );

    const clearButton = screen.getByRole('button', { name: /clear/i });
    fireEvent.click(clearButton);

    expect(useWorkspaceStore.getState().text).toBe('');
    expect(screen.getByText(/enter or paste text to get started/i)).toBeInTheDocument();
  });

  it('enables Generate Speech button when text, language, and compatible voice are present', async () => {
    const handleGenerate = vi.fn();
    const queryClient = createTestQueryClient();

    render(
      <QueryClientProvider client={queryClient}>
        <TextWorkspace onGenerate={handleGenerate} />
      </QueryClientProvider>
    );

    await waitFor(() => {
      const generateButton = screen.getByRole('button', { name: /generate speech/i });
      expect(generateButton).toBeEnabled();
    });

    const generateButton = screen.getByRole('button', { name: /generate speech/i });
    fireEvent.click(generateButton);

    expect(handleGenerate).toHaveBeenCalledWith(
      expect.objectContaining({
        text: 'Initial test text for synthesis.',
        language: 'en-US',
        voice_id: 'voice-dyn-en',
      })
    );
  });

  it('disables Generate button when text is empty', async () => {
    useWorkspaceStore.setState({ text: '' });
    const queryClient = createTestQueryClient();

    render(
      <QueryClientProvider client={queryClient}>
        <TextWorkspace />
      </QueryClientProvider>
    );

    const generateButton = screen.getByRole('button', { name: /generate speech/i });
    expect(generateButton).toBeDisabled();
    expect(screen.getByText(/please enter some text/i)).toBeInTheDocument();
  });

  it('clears incompatible voice when language changes to an unsupported locale', async () => {
    const queryClient = createTestQueryClient();
    render(
      <QueryClientProvider client={queryClient}>
        <TextWorkspace />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByDisplayValue(/english \(us\)/i)).toBeInTheDocument();
    });

    // Currently voice-dyn-en is selected. Changing language to es-ES should clear voiceId
    const langSelect = screen.getByLabelText(/speech language/i);
    fireEvent.change(langSelect, { target: { value: 'es-ES' } });

    await waitFor(() => {
      expect(useWorkspaceStore.getState().languageCode).toBe('es-ES');
      expect(useWorkspaceStore.getState().voiceId).toBe('');
    });
  });

  it('disables Generate button and flags over-limit text when character limit is exceeded', async () => {
    useWorkspaceStore.setState({ text: 'a'.repeat(2505) });
    const queryClient = createTestQueryClient();

    render(
      <QueryClientProvider client={queryClient}>
        <TextWorkspace />
      </QueryClientProvider>
    );

    const generateButton = screen.getByRole('button', { name: /generate speech/i });
    expect(generateButton).toBeDisabled();
    expect(screen.getByText(/text exceeds the maximum allowed limit/i)).toBeInTheDocument();
    expect(screen.getByText(/over limit/i)).toBeInTheDocument();
  });

  it('preserves exact user text without silently trimming during generation handoff', async () => {
    const handleGenerate = vi.fn();
    const untrimmedText = '   Hello world with intentional leading and trailing whitespace.   \n\n';
    useWorkspaceStore.setState({
      text: untrimmedText,
      languageCode: 'en-US',
      voiceId: 'voice-dyn-en',
    });
    const queryClient = createTestQueryClient();

    render(
      <QueryClientProvider client={queryClient}>
        <TextWorkspace onGenerate={handleGenerate} />
      </QueryClientProvider>
    );

    await waitFor(() => {
      const generateButton = screen.getByRole('button', { name: /generate speech/i });
      expect(generateButton).toBeEnabled();
    });

    const generateButton = screen.getByRole('button', { name: /generate speech/i });
    fireEvent.click(generateButton);

    expect(handleGenerate).toHaveBeenCalledWith(
      expect.objectContaining({
        text: untrimmedText,
        language: 'en-US',
        voice_id: 'voice-dyn-en',
      })
    );
  });

  it('renders empty voice catalog state when no voices are returned from API', async () => {
    vi.spyOn(ttsFeatureApi, 'getVoices').mockResolvedValue([]);
    useWorkspaceStore.setState({ voiceId: '' });
    const queryClient = createTestQueryClient();

    render(
      <QueryClientProvider client={queryClient}>
        <TextWorkspace />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/no voices available for language/i)).toBeInTheDocument();
    });
  });

  it('renders language error state and triggers retry', async () => {
    const errorSpy = vi.spyOn(ttsFeatureApi, 'getLanguages').mockRejectedValueOnce(new Error('Network error'));
    const queryClient = createTestQueryClient();

    render(
      <QueryClientProvider client={queryClient}>
        <TextWorkspace />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/unable to load languages/i)).toBeInTheDocument();
    });

    const retryBtn = screen.getByRole('button', { name: /retry/i });
    expect(retryBtn).toBeInTheDocument();

    errorSpy.mockResolvedValueOnce(mockLanguages);
    fireEvent.click(retryBtn);

    await waitFor(() => {
      expect(screen.getByLabelText(/speech language/i)).toBeInTheDocument();
    });
  });
});
