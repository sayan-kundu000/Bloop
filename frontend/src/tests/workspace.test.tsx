import { describe, it, expect } from 'vitest';
import { useWorkspaceStore } from '../stores/workspaceStore';
import { useAudioStore } from '../stores/audioStore';

describe('Workspace Store & Text Validation', () => {
  it('initializes with default sample and updates text stats', () => {
    const store = useWorkspaceStore.getState();
    expect(store.text.length).toBeGreaterThan(0);
    expect(store.stats.char_count).toBe(store.text.length);
    expect(store.stats.is_valid).toBe(true);
  });

  it('correctly updates character and word counts when text changes', () => {
    useWorkspaceStore.getState().setText('Hello Bloop text to speech engine');
    const state = useWorkspaceStore.getState();
    expect(state.stats.char_count).toBe(33);
    expect(state.stats.word_count).toBe(6);
    expect(state.stats.is_valid).toBe(true);
  });

  it('marks empty or whitespace text as invalid', () => {
    useWorkspaceStore.getState().setText('     ');
    const state = useWorkspaceStore.getState();
    expect(state.stats.is_valid).toBe(false);
  });

  it('clears text draft cleanly', () => {
    useWorkspaceStore.getState().clearText();
    const state = useWorkspaceStore.getState();
    expect(state.text).toBe('');
    expect(state.stats.char_count).toBe(0);
    expect(state.stats.is_valid).toBe(false);
  });
});

describe('Audio Store Playback Controls', () => {
  it('manages playback state, volume, and speed', () => {
    const audioStore = useAudioStore.getState();
    expect(audioStore.isPlaying).toBe(false);

    audioStore.playAudio('http://localhost:8000/api/v1/tts/audio/test.mp3', 'Test Track');
    const playingState = useAudioStore.getState();
    expect(playingState.isPlaying).toBe(true);
    expect(playingState.currentTitle).toBe('Test Track');

    playingStorePause: {
      useAudioStore.getState().pauseAudio();
      expect(useAudioStore.getState().isPlaying).toBe(false);
    }

    useAudioStore.getState().setSpeed(1.5);
    expect(useAudioStore.getState().speed).toBe(1.5);

    useAudioStore.getState().setVolume(0.8);
    expect(useAudioStore.getState().volume).toBe(0.8);

    useAudioStore.getState().stopAudio();
    expect(useAudioStore.getState().currentAudioUrl).toBeNull();
  });
});

describe('Voice Categorization & Dynamic Voice Architecture', () => {
  it('correctly categorizes standard studio voices and custom voices', async () => {
    const { getVoiceCategory } = await import('../components/tts/VoiceSelector');
    expect(getVoiceCategory({ voice_id: 'dynamic-voice-en-female', language_code: 'en-US' } as any)).toBe('English');
    expect(getVoiceCategory({ voice_id: 'dynamic-voice-gb-female', language_code: 'en-GB' } as any)).toBe('English');
    expect(getVoiceCategory({ voice_id: 'dynamic-voice-es-neutral', language_code: 'es-ES' } as any)).toBe('International');
    expect(getVoiceCategory({ voice_id: 'dynamic-voice-hi-neutral', language_code: 'hi-IN' } as any)).toBe('International');
    expect(getVoiceCategory({ voice_id: 'custom-voice-user', language_code: 'en-US', is_user_configured: true } as any)).toBe('Custom');
  });
});

