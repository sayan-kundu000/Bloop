import { create } from 'zustand';
import { TextStats } from '../types';
import { config as appConfig } from '../app/config';

interface WorkspaceState {
  text: string;
  languageCode: string;
  voiceId: string;
  speed: number;
  pitch: number;
  emotion: string;
  emotionId: number;
  stats: TextStats;
  setText: (text: string) => void;
  setLanguageCode: (lang: string) => void;
  setVoiceId: (voiceId: string | null) => void;
  setSpeed: (speed: number) => void;
  setPitch: (pitch: number) => void;
  setEmotion: (emotion: string, emotionId?: number) => void;
  setStats: (stats: TextStats) => void;
  clearText: () => void;
  loadSample: (sampleText: string) => void;
}

const DEFAULT_SAMPLE =
  'Welcome to Bloop. Experience high-fidelity artificial intelligence text-to-speech synthesis with dynamic voices and our integrated quantum intelligence laboratory.';

const maxLimit = appConfig?.limits?.maxTextLength || 2500;

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  text: DEFAULT_SAMPLE,
  languageCode: 'en-US',
  voiceId: '', // Default to empty string; dynamically populated from /api/v1/voices
  speed: 1.0,
  pitch: 1.0,
  emotion: 'Neutral',
  emotionId: 1,
  stats: {
    char_count: DEFAULT_SAMPLE.length,
    word_count: DEFAULT_SAMPLE.trim().split(/\s+/).length,
    estimated_duration_seconds: roundDuration(DEFAULT_SAMPLE.trim().split(/\s+/).length),
    is_valid: true,
  },

  setText: (text) => {
    const cleaned = text.trim();
    const words = cleaned ? cleaned.split(/\s+/).length : 0;
    set({
      text,
      stats: {
        char_count: text.length,
        word_count: words,
        estimated_duration_seconds: roundDuration(words),
        is_valid: cleaned.length > 0 && text.length <= maxLimit,
      },
    });
  },

  setLanguageCode: (languageCode) => set({ languageCode }),
  setVoiceId: (voiceId) => set({ voiceId: voiceId || '' }),
  setSpeed: (speed) => set({ speed }),
  setPitch: (pitch) => set({ pitch }),
  setEmotion: (emotion, emotionId = 1) => set({ emotion, emotionId }),
  setStats: (stats) => set({ stats }),
  clearText: () =>
    set({
      text: '',
      stats: {
        char_count: 0,
        word_count: 0,
        estimated_duration_seconds: 0,
        is_valid: false,
      },
    }),
  loadSample: (sampleText) => {
    const words = sampleText.trim().split(/\s+/).length;
    set({
      text: sampleText,
      stats: {
        char_count: sampleText.length,
        word_count: words,
        estimated_duration_seconds: roundDuration(words),
        is_valid: true,
      },
    });
  },
}));

function roundDuration(words: number): number {
  return Math.round((words / 2.5) * 10) / 10;
}
