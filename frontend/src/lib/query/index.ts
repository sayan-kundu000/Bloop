import { queryClient } from '../queryClient';

export { queryClient };

/**
 * Standardized Query Key Factory
 * Eliminates magic strings and guarantees consistent caching across features.
 */
export const queryKeys = {
  health: ['health'] as const,
  auth: {
    me: ['auth', 'me'] as const,
  },
  voices: {
    all: ['voices'] as const,
    byLanguage: (lang: string) => ['voices', 'language', lang] as const,
    detail: (id: string) => ['voices', 'detail', id] as const,
  },
  languages: {
    all: ['languages'] as const,
  },
  history: {
    list: (page = 1) => ['history', 'list', page] as const,
  },
  favorites: {
    list: ['favorites', 'list'] as const,
  },
  quantum: {
    circuits: ['quantum', 'circuits'] as const,
    benchmarks: ['quantum', 'benchmarks'] as const,
  },
};
