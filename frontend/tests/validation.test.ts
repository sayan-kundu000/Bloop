import { describe, it, expect } from 'vitest';
import { validateAndCalculateMetrics } from '../src/utils/validation';
import { formatDuration, formatBytes } from '../src/utils/formatters';

describe('Frontend Validation & Metric Helpers', () => {
  it('validates standard text and calculates word/character counts', () => {
    const text = 'Hello Bloop text to speech engine';
    const metrics = validateAndCalculateMetrics(text);
    expect(metrics.charCount).toBe(33);
    expect(metrics.wordCount).toBe(6);
    expect(metrics.isValid).toBe(true);
    expect(metrics.estimatedDurationSeconds).toBeGreaterThan(0);
  });

  it('rejects empty and whitespace-only text', () => {
    const metrics = validateAndCalculateMetrics('   ');
    expect(metrics.isValid).toBe(false);
    expect(metrics.charCount).toBe(0);
  });

  it('rejects text exceeding maximum limit', () => {
    const longText = 'a'.repeat(2501);
    const metrics = validateAndCalculateMetrics(longText);
    expect(metrics.isValid).toBe(false);
    expect(metrics.error).toContain('exceeds maximum limit');
  });
});

describe('Frontend Formatters', () => {
  it('formats duration in seconds to mm:ss', () => {
    expect(formatDuration(0)).toBe('00:00');
    expect(formatDuration(65)).toBe('01:05');
    expect(formatDuration(360)).toBe('06:00');
  });

  it('formats byte sizes into readable units', () => {
    expect(formatBytes(0)).toBe('0 B');
    expect(formatBytes(1024)).toBe('1 KB');
    expect(formatBytes(1048576)).toBe('1 MB');
  });
});
