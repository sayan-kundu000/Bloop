/**
 * History Feature Module
 * Manages speech generation audit trail, query hooks, filters, and mutations.
 */

export * from './hooks/useSpeechHistory';
export * from './hooks/useHistoryMutations';

// Canonical types re-exported for convenience
export type { SpeechGeneration, PaginatedResponse } from '../../types';
