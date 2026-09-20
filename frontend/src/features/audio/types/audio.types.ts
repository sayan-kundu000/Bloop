/**
 * Bloop Audio Player Domain Types
 * Defines audio sources, player lifecycle states, error representations, and control options.
 */

export interface AudioSource {
  audioUrl: string;
  downloadUrl?: string;
  title?: string;
  voiceName?: string;
  duration?: number;
  audioFormat?: string; // 'mp3' | 'wav'
  contentType?: string; // 'audio/mpeg' | 'audio/wav'
  generationId?: number | string;
  text?: string;
}

export type AudioPlayerStatus =
  | 'idle'
  | 'loading'
  | 'ready'
  | 'playing'
  | 'paused'
  | 'buffering'
  | 'ended'
  | 'error';

export type AudioPlayerErrorCode =
  | 'AUDIO_LOAD_FAILED'
  | 'AUDIO_PLAYBACK_FAILED'
  | 'AUDIO_UNSUPPORTED'
  | 'AUDIO_RESOURCE_EXPIRED'
  | 'AUDIO_NETWORK_ERROR';

export interface AudioPlayerError {
  code: AudioPlayerErrorCode;
  message: string;
  retryable: boolean;
  originalError?: unknown;
}

export type DownloadStatus = 'idle' | 'downloading' | 'downloaded' | 'error';

export interface AudioPlayerOptions {
  autoPlay?: boolean;
  initialVolume?: number; // 0.0 to 1.0
  onEnded?: () => void;
  onError?: (error: AudioPlayerError) => void;
  onTimeUpdate?: (currentTime: number, duration: number) => void;
}

export interface AudioPlayerState {
  status: AudioPlayerStatus;
  isPlaying: boolean;
  isPaused: boolean;
  isLoading: boolean;
  isBuffering: boolean;
  isEnded: boolean;
  currentTime: number;
  duration: number;
  volume: number;
  isMuted: boolean;
  error: AudioPlayerError | null;
  bufferedProgress: number; // 0 to 100
}
