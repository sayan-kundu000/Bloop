import { describe, it, expect } from 'vitest';
import {
  countCharacters,
  countWords,
  estimateDurationSeconds,
  calculateTextMetrics,
} from '../../../features/tts/utils/textMetrics';

describe('Text Metrics Calculation Utilities', () => {
  describe('countCharacters', () => {
    it('returns 0 for empty string or null/undefined', () => {
      expect(countCharacters('')).toBe(0);
      expect(countCharacters(null as unknown as string)).toBe(0);
      expect(countCharacters(undefined as unknown as string)).toBe(0);
    });

    it('returns exact character length without alteration', () => {
      expect(countCharacters('Hello')).toBe(5);
      expect(countCharacters('  Hello  ')).toBe(9);
      expect(countCharacters('Line 1\nLine 2')).toBe(13);
    });

    it('correctly handles Unicode characters and emojis', () => {
      expect(countCharacters('Hola mundo!')).toBe(11);
      expect(countCharacters('こんにちは')).toBe(5);
      expect(countCharacters('Bloop AI 🎙️')).toBe(12);
    });
  });

  describe('countWords', () => {
    it('returns 0 for empty or whitespace-only text', () => {
      expect(countWords('')).toBe(0);
      expect(countWords('   ')).toBe(0);
      expect(countWords('\n\t  \r')).toBe(0);
    });

    it('counts single words accurately', () => {
      expect(countWords('Speech')).toBe(1);
      expect(countWords('  Speech  ')).toBe(1);
    });

    it('counts multiple words separated by various whitespace characters', () => {
      expect(countWords('Bloop artificial intelligence')).toBe(3);
      expect(countWords('Bloop   artificial     intelligence')).toBe(3);
      expect(countWords('Line one\nLine two\tLine three')).toBe(6);
    });

    it('handles punctuation attached to words without counting whitespace', () => {
      expect(countWords('Hello, world! How are you today?')).toBe(6);
    });
  });

  describe('estimateDurationSeconds', () => {
    it('returns 0 when word count is 0', () => {
      expect(estimateDurationSeconds(0)).toBe(0);
      expect(estimateDurationSeconds(-5)).toBe(0);
    });

    it('estimates duration based on ~150 wpm (2.5 words/second)', () => {
      // 25 words at 2.5 words/sec = 10.0 seconds
      expect(estimateDurationSeconds(25, 1.0)).toBe(10.0);
    });

    it('adjusts duration dynamically based on playback speed factor', () => {
      // 25 words at 2.0x speed = 25 / (2.5 * 2.0) = 5.0 seconds
      expect(estimateDurationSeconds(25, 2.0)).toBe(5.0);
      // 25 words at 0.5x speed = 25 / (2.5 * 0.5) = 20.0 seconds
      expect(estimateDurationSeconds(25, 0.5)).toBe(20.0);
    });
  });

  describe('calculateTextMetrics', () => {
    it('calculates combined metrics and limit thresholds', () => {
      const metrics = calculateTextMetrics('Hello world', 100, 1.0);
      expect(metrics.characterCount).toBe(11);
      expect(metrics.wordCount).toBe(2);
      expect(metrics.estimatedDurationSeconds).toBe(0.8);
      expect(metrics.maxCharacters).toBe(100);
      expect(metrics.isNearLimit).toBe(false);
      expect(metrics.isAtLimit).toBe(false);
      expect(metrics.isOverLimit).toBe(false);
      expect(metrics.percentageUsed).toBe(11);
    });

    it('flags near limit when percentageUsed >= 85%', () => {
      const nearLimitText = 'a'.repeat(90);
      const metrics = calculateTextMetrics(nearLimitText, 100);
      expect(metrics.isNearLimit).toBe(true);
      expect(metrics.isOverLimit).toBe(false);
    });

    it('flags at limit when characterCount === maxCharacters', () => {
      const atLimitText = 'a'.repeat(100);
      const metrics = calculateTextMetrics(atLimitText, 100);
      expect(metrics.isAtLimit).toBe(true);
      expect(metrics.isOverLimit).toBe(false);
    });

    it('flags over limit when characterCount exceeds maxCharacters', () => {
      const overLimitText = 'a'.repeat(105);
      const metrics = calculateTextMetrics(overLimitText, 100);
      expect(metrics.isOverLimit).toBe(true);
      expect(metrics.isNearLimit).toBe(false);
    });
  });
});
