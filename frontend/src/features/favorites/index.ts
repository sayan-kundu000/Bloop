/**
 * Favorites Feature Module
 * Starred generations, bookmarked items, query hooks, and mutations.
 */

export * from './hooks/useFavorites';
export * from './hooks/useFavoriteMutations';

// Canonical types re-exported for convenience
export type { Favorite, SpeechGeneration, PaginatedResponse } from '../../types';
