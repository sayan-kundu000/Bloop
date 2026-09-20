import { useState, useEffect, useRef, useCallback } from 'react';
import {
  AudioSource,
  AudioPlayerState,
  AudioPlayerOptions,
  AudioPlayerError,
} from '../types/audio.types';
import { audioService } from '../services/audioService';
import { clampTime, getAudioErrorMessage } from '../utils/audioUtils';

export interface UseAudioPlayerReturn extends AudioPlayerState {
  audioRef: React.RefObject<HTMLAudioElement | null>;
  play: () => Promise<void>;
  pause: () => void;
  togglePlay: () => void;
  seek: (time: number) => void;
  setVolume: (volume: number) => void;
  toggleMute: () => void;
  restart: () => void;
  retry: () => void;
  reset: () => void;
}

export function useAudioPlayer(
  source: AudioSource | null | undefined,
  options: AudioPlayerOptions = {}
): UseAudioPlayerReturn {
  const { autoPlay = false, initialVolume = 1.0, onEnded, onError, onTimeUpdate } = options;

  // Single internal HTMLAudioElement reference
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const isMountedRef = useRef<boolean>(true);
  const prevVolumeRef = useRef<number>(initialVolume > 0 ? initialVolume : 0.8);

  // Playback state
  const [state, setState] = useState<AudioPlayerState>({
    status: 'idle',
    isPlaying: false,
    isPaused: false,
    isLoading: false,
    isBuffering: false,
    isEnded: false,
    currentTime: 0,
    duration: source?.duration || 0,
    volume: initialVolume,
    isMuted: false,
    error: null,
    bufferedProgress: 0,
  });

  const safeSetState = useCallback((updater: Partial<AudioPlayerState> | ((prev: AudioPlayerState) => AudioPlayerState)) => {
    if (isMountedRef.current) {
      setState((prev) => (typeof updater === 'function' ? updater(prev) : { ...prev, ...updater }));
    }
  }, []);

  // Initialize or update audio element when source changes
  useEffect(() => {
    isMountedRef.current = true;

    // Reset previous audio if exists
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.removeAttribute('src');
      audioRef.current.load();
    }

    if (!source || !source.audioUrl) {
      safeSetState({
        status: 'idle',
        isPlaying: false,
        isPaused: false,
        isLoading: false,
        isBuffering: false,
        isEnded: false,
        currentTime: 0,
        duration: 0,
        error: null,
        bufferedProgress: 0,
      });
      return;
    }

    const resolvedUrl = audioService.resolveUrl(source.audioUrl);

    // Instantiate or reuse audio instance
    const audio = audioRef.current || new Audio();
    audioRef.current = audio;
    audio.crossOrigin = 'use-credentials';
    audio.preload = 'metadata';
    audio.volume = state.volume;
    audio.muted = state.isMuted;

    safeSetState({
      status: 'loading',
      isLoading: true,
      isBuffering: false,
      isPlaying: false,
      isPaused: false,
      isEnded: false,
      currentTime: 0,
      duration: source.duration || 0,
      error: null,
      bufferedProgress: 0,
    });

    // Event Handlers
    const handleLoadedMetadata = () => {
      const dur = audio.duration;
      const validDuration = !isNaN(dur) && isFinite(dur) && dur > 0 ? dur : (source.duration || 0);
      safeSetState({
        duration: validDuration,
        isLoading: false,
        status: 'ready',
      });
    };

    const handleCanPlay = () => {
      safeSetState((prev) => ({
        ...prev,
        isLoading: false,
        status: prev.status === 'playing' ? 'playing' : 'ready',
      }));
    };

    const handlePlay = () => {
      safeSetState({
        isPlaying: true,
        isPaused: false,
        isEnded: false,
        status: 'playing',
      });
    };

    const handlePlaying = () => {
      safeSetState({
        isPlaying: true,
        isPaused: false,
        isBuffering: false,
        status: 'playing',
      });
    };

    const handlePause = () => {
      safeSetState((prev) => {
        // Do not switch to paused if audio ended
        if (prev.isEnded) return prev;
        return {
          ...prev,
          isPlaying: false,
          isPaused: true,
          status: 'paused',
        };
      });
    };

    const handleWaiting = () => {
      safeSetState({
        isBuffering: true,
        status: 'buffering',
      });
    };

    const handleTimeUpdate = () => {
      const current = audio.currentTime;
      const dur = audio.duration || state.duration || 0;
      safeSetState({
        currentTime: current,
        duration: !isNaN(dur) && isFinite(dur) && dur > 0 ? dur : state.duration,
      });
      if (onTimeUpdate) {
        onTimeUpdate(current, dur);
      }
    };

    const handleProgress = () => {
      if (audio.buffered.length > 0 && audio.duration > 0) {
        try {
          const bufferedEnd = audio.buffered.end(audio.buffered.length - 1);
          const percent = Math.min(100, Math.round((bufferedEnd / audio.duration) * 100));
          safeSetState({ bufferedProgress: percent });
        } catch {
          // Ignore index errors from empty buffer
        }
      }
    };

    const handleEnded = () => {
      safeSetState({
        isPlaying: false,
        isPaused: false,
        isEnded: true,
        status: 'ended',
        currentTime: audio.duration || state.duration,
      });
      if (onEnded) {
        onEnded();
      }
    };

    const handleError = () => {
      const mediaError = audio.error;
      let errorCode: AudioPlayerError['code'] = 'AUDIO_LOAD_FAILED';

      if (mediaError) {
        if (mediaError.code === MediaError.MEDIA_ERR_SRC_NOT_SUPPORTED) {
          errorCode = 'AUDIO_UNSUPPORTED';
        } else if (mediaError.code === MediaError.MEDIA_ERR_NETWORK) {
          errorCode = 'AUDIO_NETWORK_ERROR';
        }
      }

      const err: AudioPlayerError = {
        code: errorCode,
        message: getAudioErrorMessage(errorCode),
        retryable: true,
        originalError: mediaError,
      };

      safeSetState({
        status: 'error',
        isLoading: false,
        isBuffering: false,
        isPlaying: false,
        error: err,
      });

      if (onError) {
        onError(err);
      }
    };

    // Attach listeners
    audio.addEventListener('loadedmetadata', handleLoadedMetadata);
    audio.addEventListener('canplay', handleCanPlay);
    audio.addEventListener('play', handlePlay);
    audio.addEventListener('playing', handlePlaying);
    audio.addEventListener('pause', handlePause);
    audio.addEventListener('waiting', handleWaiting);
    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('progress', handleProgress);
    audio.addEventListener('ended', handleEnded);
    audio.addEventListener('error', handleError);

    // Set source and load
    audio.src = resolvedUrl;
    audio.load();

    if (autoPlay) {
      audio.play().catch((playErr) => {
        // Browser Autoplay rejection is handled gracefully
        safeSetState({
          isPlaying: false,
          isPaused: true,
          status: 'ready',
        });
      });
    }

    // Safe Cleanup on unmount or source change
    return () => {
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
      audio.removeEventListener('canplay', handleCanPlay);
      audio.removeEventListener('play', handlePlay);
      audio.removeEventListener('playing', handlePlaying);
      audio.removeEventListener('pause', handlePause);
      audio.removeEventListener('waiting', handleWaiting);
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('progress', handleProgress);
      audio.removeEventListener('ended', handleEnded);
      audio.removeEventListener('error', handleError);

      audio.pause();
      audio.removeAttribute('src');
    };
  }, [source?.audioUrl, autoPlay, source?.duration]);

  // Set unmount flag on final unmount
  useEffect(() => {
    return () => {
      isMountedRef.current = false;
      if (audioRef.current) {
        audioRef.current.pause();
      }
    };
  }, []);

  // Controls
  const play = useCallback(async () => {
    const audio = audioRef.current;
    if (!audio) return;

    try {
      safeSetState({ error: null });
      await audio.play();
    } catch (err: unknown) {
      // Handled if aborted or interrupted
      if (err instanceof DOMException && err.name === 'AbortError') {
        return;
      }
      const playerError: AudioPlayerError = {
        code: 'AUDIO_PLAYBACK_FAILED',
        message: getAudioErrorMessage('AUDIO_PLAYBACK_FAILED'),
        retryable: true,
        originalError: err,
      };
      safeSetState({
        status: 'error',
        isPlaying: false,
        error: playerError,
      });
      if (onError) onError(playerError);
    }
  }, [onError, safeSetState]);

  const pause = useCallback(() => {
    const audio = audioRef.current;
    if (!audio) return;
    audio.pause();
  }, []);

  const togglePlay = useCallback(() => {
    if (state.isPlaying) {
      pause();
    } else {
      if (state.isEnded) {
        restart();
      } else {
        play();
      }
    }
  }, [state.isPlaying, state.isEnded, pause, play]);

  const seek = useCallback((time: number) => {
    const audio = audioRef.current;
    if (!audio) return;

    const clamped = clampTime(time, state.duration || audio.duration || 0);
    audio.currentTime = clamped;
    safeSetState({ currentTime: clamped, isEnded: false });
  }, [state.duration, safeSetState]);

  const setVolume = useCallback((vol: number) => {
    const audio = audioRef.current;
    const clamped = Math.max(0, Math.min(1, vol));
    if (audio) {
      audio.volume = clamped;
      audio.muted = clamped === 0;
    }
    if (clamped > 0) {
      prevVolumeRef.current = clamped;
    }
    safeSetState({ volume: clamped, isMuted: clamped === 0 });
  }, [safeSetState]);

  const toggleMute = useCallback(() => {
    const audio = audioRef.current;
    if (!audio) return;

    if (state.isMuted || state.volume === 0) {
      // Unmute: restore previous non-zero volume
      const restored = prevVolumeRef.current > 0 ? prevVolumeRef.current : 0.8;
      audio.muted = false;
      audio.volume = restored;
      safeSetState({ isMuted: false, volume: restored });
    } else {
      // Mute: save current volume
      prevVolumeRef.current = state.volume;
      audio.muted = true;
      safeSetState({ isMuted: true });
    }
  }, [state.isMuted, state.volume, safeSetState]);

  const restart = useCallback(() => {
    const audio = audioRef.current;
    if (!audio) return;
    audio.currentTime = 0;
    safeSetState({ currentTime: 0, isEnded: false });
    play();
  }, [play, safeSetState]);

  const retry = useCallback(() => {
    const audio = audioRef.current;
    if (!audio || !source?.audioUrl) return;
    safeSetState({ error: null, isLoading: true, status: 'loading' });
    const resolvedUrl = audioService.resolveUrl(source.audioUrl);
    audio.src = resolvedUrl;
    audio.load();
    play();
  }, [source?.audioUrl, play, safeSetState]);

  const reset = useCallback(() => {
    const audio = audioRef.current;
    if (audio) {
      audio.pause();
      audio.currentTime = 0;
    }
    safeSetState({
      status: 'idle',
      isPlaying: false,
      isPaused: false,
      isLoading: false,
      isBuffering: false,
      isEnded: false,
      currentTime: 0,
      error: null,
    });
  }, [safeSetState]);

  return {
    ...state,
    audioRef,
    play,
    pause,
    togglePlay,
    seek,
    setVolume,
    toggleMute,
    restart,
    retry,
    reset,
  };
}
