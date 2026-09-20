import { User, UserPreference, SpeechGeneration, Voice, Language } from '../../types';

export const mockUser: User = {
  id: 1,
  email: 'tester@example.com',
  full_name: 'Test Engineer',
  is_active: true,
  is_superuser: false,
  created_at: '2026-09-17T12:00:00Z',
};

export const mockPreferences: UserPreference = {
  id: 1,
  user_id: 1,
  theme: 'dark',
  audio_speed: 1.0,
  auto_play: false,
  default_language_code: 'en-US',
  default_voice_id: null,
};

export const mockLanguages: Language[] = [
  { code: 'en-US', name: 'English (US)', is_active: true },
  { code: 'es-ES', name: 'Spanish (Spain)', is_active: true },
];

/**
 * Dynamic test voice fixtures without actual ElevenLabs production voice IDs
 */
export const mockDynamicVoices: Voice[] = [
  {
    id: 101,
    voice_id: 'dynamic-test-voice-1',
    name: 'Dynamic Test Voice 1',
    language_code: 'en-US',
    gender: 'neutral',
    provider: 'elevenlabs',
    is_active: true,
    is_user_configured: false,
  },
];

export const mockEmptyVoices: Voice[] = [];

export const mockGeneration: SpeechGeneration = {
  id: 1,
  user_id: 1,
  text: 'Hello from Bloop test harness.',
  char_count: 31,
  word_count: 6,
  language_code: 'en-US',
  voice_id: 'dynamic-test-voice-1',
  voice_name: 'Dynamic Test Voice 1',
  audio_url: '/api/v1/audio/1/play',
  download_url: '/api/v1/audio/1/download',
  duration_seconds: 2.5,
  file_size_bytes: 40960,
  provider: 'elevenlabs',
  is_favorite: false,
  created_at: '2026-09-17T12:05:00Z',
};
