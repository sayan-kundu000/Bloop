import { describe, it, expect } from 'vitest';
import {
  formatDuration,
  clampTime,
  resolveMimeExtension,
  sanitizeFilename,
  getAudioErrorMessage,
} from '../../../features/audio/utils/audioUtils';

describe('Audio Utilities (Prompt 20)', () => {
  describe('formatDuration', () => {
    it('formats zero seconds as 00:00', () => {
      expect(formatDuration(0)).toBe('00:00');
    });

    it('formats single-digit seconds with leading zeros', () => {
      expect(formatDuration(5)).toBe('00:05');
    });

    it('formats seconds over one minute correctly', () => {
      expect(formatDuration(65)).toBe('01:05');
      expect(formatDuration(125)).toBe('02:05');
    });

    it('formats hours correctly when duration exceeds 3600 seconds', () => {
      expect(formatDuration(3665)).toBe('01:01:05');
      expect(formatDuration(7322)).toBe('02:02:02');
    });

    it('handles negative, NaN, Infinity and null/undefined values safely without crashing', () => {
      expect(formatDuration(-10)).toBe('00:00');
      expect(formatDuration(NaN)).toBe('00:00');
      expect(formatDuration(Infinity)).toBe('00:00');
      expect(formatDuration(-Infinity)).toBe('00:00');
      expect(formatDuration(null)).toBe('00:00');
      expect(formatDuration(undefined)).toBe('00:00');
    });
  });

  describe('clampTime', () => {
    it('clamps time within 0 and duration', () => {
      expect(clampTime(15, 60)).toBe(15);
      expect(clampTime(-5, 60)).toBe(0);
      expect(clampTime(75, 60)).toBe(60);
    });

    it('handles invalid duration or zero duration safely', () => {
      expect(clampTime(10, 0)).toBe(0);
      expect(clampTime(10, -5)).toBe(0);
      expect(clampTime(10, NaN)).toBe(0);
      expect(clampTime(NaN, 60)).toBe(0);
    });
  });

  describe('resolveMimeExtension', () => {
    it('resolves mp3 for audio/mpeg, mp3 format, or fallback', () => {
      expect(resolveMimeExtension('audio/mpeg')).toBe('mp3');
      expect(resolveMimeExtension('audio/mp3')).toBe('mp3');
      expect(resolveMimeExtension(undefined, 'mp3')).toBe('mp3');
      expect(resolveMimeExtension(undefined, undefined)).toBe('mp3');
    });

    it('resolves wav for audio/wav or wav format', () => {
      expect(resolveMimeExtension('audio/wav')).toBe('wav');
      expect(resolveMimeExtension('audio/wave')).toBe('wav');
      expect(resolveMimeExtension(undefined, 'wav')).toBe('wav');
    });

    it('resolves ogg, webm, flac, and aac properly', () => {
      expect(resolveMimeExtension('audio/ogg')).toBe('ogg');
      expect(resolveMimeExtension('audio/webm')).toBe('webm');
      expect(resolveMimeExtension('audio/flac')).toBe('flac');
      expect(resolveMimeExtension('audio/aac')).toBe('aac');
    });
  });

  describe('sanitizeFilename', () => {
    it('returns default fallback when name is empty', () => {
      expect(sanitizeFilename('', 'bloop-speech', 'mp3')).toBe('bloop-speech.mp3');
      expect(sanitizeFilename(undefined, 'bloop-speech', 'mp3')).toBe('bloop-speech.mp3');
    });

    it('neutralizes path traversal attempts like ../../evil', () => {
      const sanitized = sanitizeFilename('../../etc/passwd', 'bloop-speech', 'mp3');
      expect(sanitized).not.toContain('..');
      expect(sanitized).not.toContain('/');
      expect(sanitized).toBe('etcpasswd.mp3');
    });

    it('removes illegal filesystem characters (<>:"/\\|?*) and normalizes whitespace', () => {
      const sanitized = sanitizeFilename('Speech: "My Test" <Audio>?', 'fallback', 'mp3');
      expect(sanitized).toBe('Speech-My-Test-Audio.mp3');
    });

    it('truncates excessively long names to 60 characters while preserving extension', () => {
      const superLong = 'a'.repeat(120);
      const sanitized = sanitizeFilename(superLong, 'bloop-speech', 'mp3');
      expect(sanitized.length).toBeLessThanOrEqual(64); // 60 chars + .mp3
      expect(sanitized.endsWith('.mp3')).toBe(true);
    });

    it('avoids double extension if extension already present', () => {
      expect(sanitizeFilename('my-speech.mp3', 'bloop-speech', 'mp3')).toBe('my-speech.mp3');
    });
  });

  describe('getAudioErrorMessage', () => {
    it('returns clear, friendly messages for all standard audio error codes', () => {
      expect(getAudioErrorMessage('AUDIO_LOAD_FAILED')).toContain('could not be loaded');
      expect(getAudioErrorMessage('AUDIO_PLAYBACK_FAILED')).toContain('Playback failed to start');
      expect(getAudioErrorMessage('AUDIO_UNSUPPORTED')).toContain('does not support this audio format');
      expect(getAudioErrorMessage('AUDIO_RESOURCE_EXPIRED')).toContain('expired');
      expect(getAudioErrorMessage('AUDIO_NETWORK_ERROR')).toContain('Network connection interrupted');
    });
  });
});
