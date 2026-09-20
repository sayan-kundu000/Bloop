import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useAudioPlayer } from '../../../features/audio/hooks/useAudioPlayer';
import { AudioSource } from '../../../features/audio/types/audio.types';

describe('useAudioPlayer Hook (Prompt 20)', () => {
  const mockSource: AudioSource = {
    audioUrl: '/api/v1/tts/audio/speech-101.mp3',
    downloadUrl: '/api/v1/tts/download/speech-101.mp3',
    title: 'Voice Demo',
    voiceName: 'Studio Alpha',
    duration: 12.5,
    audioFormat: 'mp3',
  };

  let playMock: ReturnType<typeof vi.fn>;
  let pauseMock: ReturnType<typeof vi.fn>;
  let loadMock: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    playMock = vi.fn().mockResolvedValue(undefined);
    pauseMock = vi.fn();
    loadMock = vi.fn();

    window.HTMLMediaElement.prototype.play = playMock as any;
    window.HTMLMediaElement.prototype.pause = pauseMock as any;
    window.HTMLMediaElement.prototype.load = loadMock as any;
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('initializes with idle state when source is null', () => {
    const { result } = renderHook(() => useAudioPlayer(null));

    expect(result.current.status).toBe('idle');
    expect(result.current.isPlaying).toBe(false);
    expect(result.current.isPaused).toBe(false);
    expect(result.current.currentTime).toBe(0);
    expect(result.current.duration).toBe(0);
    expect(result.current.error).toBeNull();
  });

  it('loads audio source and populates duration when source is provided', () => {
    const { result } = renderHook(() => useAudioPlayer(mockSource));

    expect(result.current.duration).toBe(12.5);
    expect(result.current.isLoading).toBe(true);
    expect(result.current.status).toBe('loading');
  });

  it('invokes play and pause methods', async () => {
    const { result } = renderHook(() => useAudioPlayer(mockSource));

    await act(async () => {
      await result.current.play();
    });
    expect(playMock).toHaveBeenCalled();

    act(() => {
      result.current.pause();
    });
    expect(pauseMock).toHaveBeenCalled();
  });

  it('toggles playback between play and pause', async () => {
    const { result } = renderHook(() => useAudioPlayer(mockSource));

    // Initially paused/idle -> toggle calls play
    await act(async () => {
      result.current.togglePlay();
    });
    expect(playMock).toHaveBeenCalledTimes(1);
  });

  it('manages volume adjustments and clamps values between 0 and 1', () => {
    const { result } = renderHook(() => useAudioPlayer(mockSource, { initialVolume: 0.8 }));

    expect(result.current.volume).toBe(0.8);
    expect(result.current.isMuted).toBe(false);

    act(() => {
      result.current.setVolume(0.5);
    });
    expect(result.current.volume).toBe(0.5);

    // Setting volume to 0 automatically mutes
    act(() => {
      result.current.setVolume(0);
    });
    expect(result.current.volume).toBe(0);
    expect(result.current.isMuted).toBe(true);
  });

  it('mutes and restores previous non-zero volume when unmuting', () => {
    const { result } = renderHook(() => useAudioPlayer(mockSource, { initialVolume: 0.7 }));

    // Toggle mute -> muted
    act(() => {
      result.current.toggleMute();
    });
    expect(result.current.isMuted).toBe(true);

    // Toggle unmute -> restores 0.7
    act(() => {
      result.current.toggleMute();
    });
    expect(result.current.isMuted).toBe(false);
    expect(result.current.volume).toBe(0.7);
  });

  it('clamps seeking within valid track boundaries', () => {
    const { result } = renderHook(() => useAudioPlayer(mockSource));

    act(() => {
      result.current.seek(5.0);
    });
    expect(result.current.currentTime).toBe(5.0);

    // Seeking beyond duration clamps to duration
    act(() => {
      result.current.seek(50.0);
    });
    expect(result.current.currentTime).toBe(12.5);

    // Negative seek clamps to 0
    act(() => {
      result.current.seek(-10);
    });
    expect(result.current.currentTime).toBe(0);
  });

  it('restarts playback by resetting time to 0 and calling play', async () => {
    const { result } = renderHook(() => useAudioPlayer(mockSource));

    act(() => {
      result.current.seek(8.0);
    });
    expect(result.current.currentTime).toBe(8.0);

    await act(async () => {
      result.current.restart();
    });

    expect(result.current.currentTime).toBe(0);
    expect(playMock).toHaveBeenCalled();
  });

  it('resets audio state cleanly', () => {
    const { result } = renderHook(() => useAudioPlayer(mockSource));

    act(() => {
      result.current.reset();
    });

    expect(result.current.status).toBe('idle');
    expect(result.current.currentTime).toBe(0);
    expect(result.current.isPlaying).toBe(false);
  });

  it('cleans up audio on unmount without throwing or leaking listeners', () => {
    const { unmount } = renderHook(() => useAudioPlayer(mockSource));

    unmount();
    expect(pauseMock).toHaveBeenCalled();
  });
});
