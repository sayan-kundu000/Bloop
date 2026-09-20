import { describe, it, expect } from 'vitest';
import { config, normalizeApiUrl } from '../src/app/config';

describe('Frontend Configuration Module', () => {
  it('normalizes API URLs correctly', () => {
    expect(normalizeApiUrl('http://localhost:8000/')).toBe('http://localhost:8000');
    expect(normalizeApiUrl('https://api.bloop.com///')).toBe('https://api.bloop.com');
    expect(normalizeApiUrl('')).toBe('http://localhost:8000');
    expect(normalizeApiUrl('   ')).toBe('http://localhost:8000');
    expect(normalizeApiUrl('http://127.0.0.1:8000')).toBe('http://127.0.0.1:8000');
  });

  it('provides immutable runtime configuration', () => {
    expect(Object.isFrozen(config)).toBe(true);
    expect(() => {
      // @ts-expect-error - runtime immutability test
      config.apiBaseUrl = 'http://hacked.com';
    }).toThrow();
  });

  it('exposes valid API endpoints', () => {
    expect(config.apiBaseUrl).toBeTruthy();
    expect(config.apiBaseUrl.endsWith('/')).toBe(false);
    expect(config.apiV1Url).toBe(`${config.apiBaseUrl}/api/v1`);
  });

  it('exposes typed environment flags', () => {
    expect(['development', 'test', 'production']).toContain(config.environment);
    expect(typeof config.isProduction).toBe('boolean');
    expect(typeof config.isDevelopment).toBe('boolean');
    expect(typeof config.isTest).toBe('boolean');
  });

  it('maintains system constraints and limits', () => {
    expect(config.limits.minTextLength).toBe(1);
    expect(config.limits.maxTextLength).toBe(2500);
    expect(config.limits.defaultSpeechRate).toBe(1.0);
    expect(config.limits.defaultPitch).toBe(1.0);
  });

  it('GUARANTEE: frontend configuration contains zero backend secrets', () => {
    const configKeys = Object.keys(config);
    const forbiddenSubstrings = [
      'ELEVENLABS',
      'DATABASE',
      'SECRET',
      'PASSWORD',
      'PRIVATE',
      'TOKEN_KEY',
    ];

    for (const key of configKeys) {
      for (const forbidden of forbiddenSubstrings) {
        expect(key.toUpperCase()).not.toContain(forbidden);
      }
    }
  });
});
