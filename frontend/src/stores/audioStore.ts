import { create } from 'zustand';

interface AudioState {
  currentAudioUrl: string | null;
  currentTitle: string | null;
  isPlaying: boolean;
  duration: number;
  currentTime: number;
  volume: number;
  speed: number;
  playAudio: (url: string, title?: string) => void;
  pauseAudio: () => void;
  togglePlay: () => void;
  setCurrentTime: (time: number) => void;
  setDuration: (duration: number) => void;
  setVolume: (volume: number) => void;
  setSpeed: (speed: number) => void;
  stopAudio: () => void;
}

export const useAudioStore = create<AudioState>((set, get) => ({
  currentAudioUrl: null,
  currentTitle: null,
  isPlaying: false,
  duration: 0,
  currentTime: 0,
  volume: 1.0,
  speed: 1.0,

  playAudio: (url: string, title?: string) => {
    set({
      currentAudioUrl: url,
      currentTitle: title || 'Generated Audio',
      isPlaying: true,
      currentTime: 0,
    });
  },

  pauseAudio: () => set({ isPlaying: false }),

  togglePlay: () => {
    const { isPlaying, currentAudioUrl } = get();
    if (!currentAudioUrl) return;
    set({ isPlaying: !isPlaying });
  },

  setCurrentTime: (time: number) => set({ currentTime: time }),
  setDuration: (duration: number) => set({ duration }),
  setVolume: (volume: number) => set({ volume }),
  setSpeed: (speed: number) => set({ speed }),
  stopAudio: () => set({ isPlaying: false, currentAudioUrl: null, currentTime: 0 }),
}));
