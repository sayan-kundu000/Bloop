import { describe, it, expect } from 'vitest';
import { queryKeys } from '../../src/lib/query';
import { config } from '../../src/app/config';

describe('Feature Architecture & Query Keys', () => {
  it('defines hierarchical, predictable query keys for all feature domains', () => {
    expect(queryKeys.health).toEqual(['health']);
    expect(queryKeys.auth.me).toEqual(['auth', 'me']);
    expect(queryKeys.voices.all).toEqual(['voices']);
    expect(queryKeys.voices.byLanguage('en-US')).toEqual(['voices', 'language', 'en-US']);
    expect(queryKeys.languages.all).toEqual(['languages']);
    expect(queryKeys.history.list(2)).toEqual(['history', 'list', 2]);
    expect(queryKeys.favorites.list).toEqual(['favorites', 'list']);
    expect(queryKeys.quantum.circuits).toEqual(['quantum', 'circuits']);
  });

  it('loads typed runtime application configuration properly', () => {
    expect(config.apiBaseUrl).toBeDefined();
    expect(config.limits.maxTextLength).toBe(2500);
    expect(config.queryClient.retryCount).toBe(1);
  });
});
