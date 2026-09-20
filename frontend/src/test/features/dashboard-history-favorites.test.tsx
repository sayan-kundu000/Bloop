import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { DashboardPage } from '../../pages/DashboardPage';
import { HistoryPage } from '../../pages/HistoryPage';
import { FavoritesPage } from '../../pages/FavoritesPage';
import { HistoryDetailPage } from '../../pages/HistoryDetailPage';
import { Navbar } from '../../components/common/Navbar';
import { historyApi, voiceApi, quantumApi } from '../../api/client';
import { useAuthStore } from '../../stores/authStore';
import { useWorkspaceStore } from '../../stores/workspaceStore';
import { useAudioStore } from '../../stores/audioStore';
import { queryClient } from '../../lib/queryClient';
import { SpeechGeneration, Favorite } from '../../types';

// Mock API Client
vi.mock('../../api/client', () => ({
  authApi: {
    login: vi.fn(),
    register: vi.fn(),
    logout: vi.fn().mockResolvedValue(undefined),
    getCurrentUser: vi.fn(),
  },
  historyApi: {
    getHistory: vi.fn(),
    getGeneration: vi.fn(),
    deleteGeneration: vi.fn(),
    getFavorites: vi.fn(),
    addFavorite: vi.fn(),
    removeFavorite: vi.fn(),
    removeFavoriteByGeneration: vi.fn(),
  },
  voiceApi: {
    getLanguages: vi.fn(),
    getVoices: vi.fn(),
  },
  quantumApi: {
    getHistory: vi.fn(),
  },
  ttsApi: {
    getAudioUrl: vi.fn((url: string) => `http://localhost:8000${url}`),
  },
}));

const mockGeneration: SpeechGeneration = {
  id: 42,
  user_id: 1,
  text: 'The quantum architecture of sound transcends classical barriers.',
  char_count: 65,
  word_count: 8,
  language_code: 'en-US',
  voice_id: 'voice-aria-01',
  voice_name: 'Aria Neural',
  audio_url: '/api/v1/tts/audio/speech-42.mp3',
  download_url: '/api/v1/tts/download/speech-42.mp3',
  duration_seconds: 3.4,
  file_size_bytes: 48120,
  provider: 'elevenlabs',
  is_favorite: false,
  created_at: '2026-09-19T10:00:00Z',
};

const mockFavoriteGen: SpeechGeneration = {
  ...mockGeneration,
  id: 43,
  text: 'Bookmarked favorite speech synthesis with crystal fidelity.',
  is_favorite: true,
  favorite_id: 7,
};

const mockFavoriteRecord: Favorite = {
  id: 7,
  user_id: 1,
  generation_id: 43,
  label: 'Keynote audio',
  created_at: '2026-09-19T10:30:00Z',
  generation: mockFavoriteGen,
};

function renderWithProviders(ui: React.ReactElement, initialRoute = '/') {
  const testQueryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  return render(
    <QueryClientProvider client={testQueryClient}>
      <MemoryRouter initialEntries={[initialRoute]}>
        {ui}
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe('Prompt 21 — Bloop Navigation Experience', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useAuthStore.setState({
      user: { id: 1, email: 'test@bloop.ai', full_name: 'Ada Lovelace', is_active: true, is_superuser: false, created_at: '' },
      token: 'mock-jwt-token',
      isAuthenticated: true,
      isLoading: false,
    });
  });

  it('renders primary navigation links and indicates active route', () => {
    renderWithProviders(<Navbar />, '/dashboard');

    expect(screen.getByRole('banner')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Create Speech')).toBeInTheDocument();
    expect(screen.getByText('History')).toBeInTheDocument();
    expect(screen.getByText('Favorites')).toBeInTheDocument();
    expect(screen.getByText('Quantum Lab')).toBeInTheDocument();

    const dashboardLink = screen.getByRole('link', { name: /^dashboard$/i });
    expect(dashboardLink).toHaveAttribute('aria-current', 'page');
  });

  it('correctly identifies history as active on nested route /history/42', () => {
    renderWithProviders(<Navbar />, '/history/42');

    const historyLink = screen.getByRole('link', { name: /^history$/i });
    expect(historyLink).toHaveAttribute('aria-current', 'page');
  });

  it('toggles mobile navigation menu and closes on escape key', () => {
    renderWithProviders(<Navbar />, '/dashboard');

    const menuToggle = screen.getByLabelText(/open menu/i);
    fireEvent.click(menuToggle);

    expect(screen.getByRole('navigation', { name: /mobile navigation/i })).toBeInTheDocument();

    fireEvent.keyDown(window, { key: 'Escape' });
    expect(screen.queryByRole('navigation', { name: /mobile navigation/i })).not.toBeInTheDocument();
  });

  it('clears query cache and stops audio playback upon logout', async () => {
    const clearSpy = vi.spyOn(queryClient, 'clear');
    const stopAudioSpy = vi.spyOn(useAudioStore.getState(), 'stopAudio');

    renderWithProviders(<Navbar />, '/dashboard');

    const logoutButtons = screen.getAllByTitle(/sign out/i);
    fireEvent.click(logoutButtons[0]);

    expect(clearSpy).toHaveBeenCalled();
    expect(stopAudioSpy).toHaveBeenCalled();
    expect(useAuthStore.getState().isAuthenticated).toBe(false);
  });
});

describe('Prompt 21 — Dashboard Experience', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useAuthStore.setState({
      user: { id: 1, email: 'creator@bloop.ai', full_name: 'Elena Rostova', is_active: true, is_superuser: false, created_at: '' },
      token: 'valid-token',
      isAuthenticated: true,
      isLoading: false,
    });

    vi.mocked(voiceApi.getVoices).mockResolvedValue([
      { id: 1, voice_id: 'v1', name: 'Aria', language_code: 'en-US', gender: 'female', provider: 'elevenlabs', is_active: true, is_user_configured: false },
    ]);
    vi.mocked(quantumApi.getHistory).mockResolvedValue([]);
  });

  it('renders personalized welcome and summary metrics', async () => {
    vi.mocked(historyApi.getHistory).mockResolvedValue({
      items: [mockGeneration],
      total: 14,
      page: 1,
      page_size: 4,
      has_next: true,
    });
    vi.mocked(historyApi.getFavorites).mockResolvedValue({
      items: [mockFavoriteRecord],
      total: 3,
      page: 1,
      page_size: 4,
      has_next: false,
    });

    renderWithProviders(<DashboardPage />);

    await waitFor(() => {
      expect(screen.getByText(/welcome back,/i)).toBeInTheDocument();
      expect(screen.getByText('Elena Rostova')).toBeInTheDocument();
      expect(screen.getByText('14')).toBeInTheDocument();
      expect(screen.getByText('3')).toBeInTheDocument();
    });
  });

  it('renders recent generations and allows immediate audio playback', async () => {
    vi.mocked(historyApi.getHistory).mockResolvedValue({
      items: [mockGeneration],
      total: 1,
      page: 1,
      page_size: 4,
      has_next: false,
    });
    vi.mocked(historyApi.getFavorites).mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 4,
      has_next: false,
    });

    const playAudioSpy = vi.spyOn(useAudioStore.getState(), 'playAudio');

    renderWithProviders(<DashboardPage />);

    await waitFor(() => {
      expect(screen.getByText(/The quantum architecture of sound transcends classical barriers/i)).toBeInTheDocument();
    });

    const playButton = screen.getByRole('button', { name: new RegExp(`Play generation ${mockGeneration.id}`, 'i') });
    fireEvent.click(playButton);

    expect(playAudioSpy).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/tts/audio/speech-42.mp3',
      'Aria Neural'
    );
  });

  it('displays graceful empty states when user has zero generations and favorites', async () => {
    vi.mocked(historyApi.getHistory).mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 4,
      has_next: false,
    });
    vi.mocked(historyApi.getFavorites).mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 4,
      has_next: false,
    });

    renderWithProviders(<DashboardPage />);

    await waitFor(() => {
      expect(screen.getByText(/no speech generations yet/i)).toBeInTheDocument();
      expect(screen.getByText(/no bookmarked favorites yet/i)).toBeInTheDocument();
      expect(screen.getByText(/create your first speech/i)).toBeInTheDocument();
    });
  });
});

describe('Prompt 21 — Speech History & Favorites Experience', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(voiceApi.getLanguages).mockResolvedValue([
      { code: 'en-US', name: 'English (US)', is_active: true },
      { code: 'fr-FR', name: 'French (FR)', is_active: true },
    ]);
  });

  it('renders speech history with search, filtering, and pagination', async () => {
    vi.mocked(historyApi.getHistory).mockResolvedValue({
      items: [mockGeneration],
      total: 25,
      page: 1,
      page_size: 12,
      has_next: true,
    });

    renderWithProviders(<HistoryPage />, '/history');

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /speech generation history/i })).toBeInTheDocument();
      expect(screen.getByText(/The quantum architecture of sound/i)).toBeInTheDocument();
      expect(screen.getByText(/showing/i)).toBeInTheDocument();
      expect(screen.getByText('25')).toBeInTheDocument();
    });

    // Test debounced search
    const searchInput = screen.getByLabelText(/search speech history/i);
    fireEvent.change(searchInput, { target: { value: 'quantum sound' } });

    await waitFor(() => {
      expect(historyApi.getHistory).toHaveBeenCalledWith(
        expect.objectContaining({
          search: 'quantum sound',
        })
      );
    });
  });

  it('allows "Use as New" action to load historical generation into workspace store', async () => {
    vi.mocked(historyApi.getHistory).mockResolvedValue({
      items: [mockGeneration],
      total: 1,
      page: 1,
      page_size: 12,
      has_next: false,
    });

    renderWithProviders(<HistoryPage />, '/history');

    await waitFor(() => {
      expect(screen.getByText(/The quantum architecture of sound/i)).toBeInTheDocument();
    });

    const useAsNewBtn = screen.getByLabelText(new RegExp(`use generation ${mockGeneration.id} text as new draft in workspace`, 'i'));
    fireEvent.click(useAsNewBtn);

    expect(useWorkspaceStore.getState().text).toBe(mockGeneration.text);
    expect(useWorkspaceStore.getState().languageCode).toBe(mockGeneration.language_code);
    expect(useWorkspaceStore.getState().voiceId).toBe(mockGeneration.voice_id);
  });

  it('renders favorites page and supports unstarring a favorite record', async () => {
    vi.mocked(historyApi.getFavorites).mockResolvedValue({
      items: [mockFavoriteRecord],
      total: 1,
      page: 1,
      page_size: 12,
      has_next: false,
    });
    vi.mocked(historyApi.removeFavorite).mockResolvedValue(undefined);

    renderWithProviders(<FavoritesPage />, '/favorites');

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /starred favorites/i })).toBeInTheDocument();
      expect(screen.getByText(/Bookmarked favorite speech synthesis/i)).toBeInTheDocument();
    });

    const favoriteBtn = screen.getByRole('button', { name: /remove.*from.*favorites/i });
    fireEvent.click(favoriteBtn);

    await waitFor(() => {
      expect(historyApi.removeFavorite).toHaveBeenCalledWith(mockFavoriteRecord.id);
    });
  });
});

describe('Prompt 21 — Generation Detail & AudioPlayer Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('loads generation detail and embeds Prompt 20 AudioPlayer', async () => {
    vi.mocked(historyApi.getGeneration).mockResolvedValue(mockGeneration);

    renderWithProviders(
      <Routes>
        <Route path="/history/:id" element={<HistoryDetailPage />} />
      </Routes>,
      '/history/42'
    );

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /speech generation #42/i })).toBeInTheDocument();
      expect(screen.getByText(/The quantum architecture of sound transcends classical barriers/i)).toBeInTheDocument();
      // AudioPlayer region from Prompt 20
      expect(screen.getByRole('region', { name: /bloop audio player/i })).toBeInTheDocument();
    });
  });

  it('displays graceful not-found state when generation ID does not exist', async () => {
    vi.mocked(historyApi.getGeneration).mockRejectedValue(new Error('Generation not found or unauthorized.'));

    renderWithProviders(
      <Routes>
        <Route path="/history/:id" element={<HistoryDetailPage />} />
      </Routes>,
      '/history/999'
    );

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /generation record not found/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /return to speech history/i })).toBeInTheDocument();
    });
  });
});
