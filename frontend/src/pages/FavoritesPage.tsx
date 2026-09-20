import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  Star,
  Search,
  Globe,
  ChevronLeft,
  ChevronRight,
  RefreshCw,
  X,
  AlertTriangle,
  RotateCcw,
} from 'lucide-react';
import { voiceApi } from '../api/client';
import { useFavorites, useRemoveFavoriteMutation } from '../features/favorites';
import { useDeleteGenerationMutation } from '../features/history';
import { GenerationCard } from '../components/tts/GenerationCard';
import { GenerationDetailModal } from '../components/tts/GenerationDetailModal';
import { SpeechGeneration } from '../types';

export const FavoritesPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  const initialSearch = searchParams.get('search') || '';
  const initialLang = searchParams.get('language') || '';
  const initialPage = parseInt(searchParams.get('page') || '1', 10) || 1;

  const [searchTerm, setSearchTerm] = useState(initialSearch);
  const [debouncedSearch, setDebouncedSearch] = useState(initialSearch);
  const [selectedLang, setSelectedLang] = useState(initialLang);
  const [page, setPage] = useState(initialPage);

  // Detail Modal state
  const [selectedGen, setSelectedGen] = useState<SpeechGeneration | null>(null);

  // Dynamic Languages catalogue (Prompt 21 §114)
  const { data: languages = [] } = useQuery({
    queryKey: ['languages'],
    queryFn: () => voiceApi.getLanguages(),
    staleTime: 1000 * 60 * 10,
  });

  // Debounce search input (300ms)
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(searchTerm.trim());
      setPage(1);
    }, 300);
    return () => clearTimeout(handler);
  }, [searchTerm]);

  // Sync state to URL search parameters
  useEffect(() => {
    const params: Record<string, string> = {};
    if (debouncedSearch) params.search = debouncedSearch;
    if (selectedLang) params.language = selectedLang;
    if (page > 1) params.page = page.toString();

    setSearchParams(params, { replace: true });
  }, [debouncedSearch, selectedLang, page, setSearchParams]);

  // Query hook using features/favorites abstraction
  const { data, isLoading, refetch, isFetching, isError, error } = useFavorites({
    search: debouncedSearch || undefined,
    language: selectedLang || undefined,
    page,
    page_size: 12,
  });

  const removeFavoriteMutation = useRemoveFavoriteMutation();
  const deleteGenerationMutation = useDeleteGenerationMutation();

  const favorites = data?.items || [];
  const total = data?.total || 0;
  const totalPages = Math.ceil(total / 12) || 1;

  const hasActiveFilters = Boolean(searchTerm || selectedLang);

  const resetFilters = () => {
    setSearchTerm('');
    setDebouncedSearch('');
    setSelectedLang('');
    setPage(1);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center space-x-3">
            <Star className="w-8 h-8 text-amber-400 fill-amber-400" aria-hidden="true" />
            <span>Starred <span className="gradient-text-bloop">Favorites</span></span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Access, inspect, replay, and manage your bookmarked high-priority speech generations.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <Link
            to="/history"
            className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-white/10 text-xs font-medium transition"
          >
            All History
          </Link>

          <button
            onClick={() => refetch()}
            disabled={isFetching}
            className="flex items-center space-x-2 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-white/10 text-xs font-medium transition disabled:opacity-50"
            title="Refresh favorites records"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isFetching ? 'animate-spin' : ''}`} aria-hidden="true" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Search & Filter Bar within Favorites (Prompt 21 §36) */}
      <div className="glass-panel rounded-2xl p-4 border border-white/10 mb-8 flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
        {/* Search input */}
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" aria-hidden="true" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search favorites by text, voice name, or bookmark label..."
            aria-label="Search favorites"
            className="w-full bg-slate-900/90 text-xs text-white rounded-xl pl-10 pr-10 py-2.5 border border-white/10 focus:outline-none focus:border-bloop-500 transition"
          />
          {searchTerm && (
            <button
              onClick={() => setSearchTerm('')}
              aria-label="Clear search text"
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
            >
              <X className="w-3.5 h-3.5" aria-hidden="true" />
            </button>
          )}
        </div>

        {/* Language Filter */}
        <div className="flex items-center space-x-2">
          <Globe className="w-4 h-4 text-slate-400 shrink-0" aria-hidden="true" />
          <select
            value={selectedLang}
            onChange={(e) => {
              setSelectedLang(e.target.value);
              setPage(1);
            }}
            aria-label="Filter favorites by language"
            className="bg-slate-900/90 text-xs text-white rounded-xl px-3 py-2.5 border border-white/10 focus:outline-none focus:border-bloop-500 cursor-pointer min-w-36"
          >
            <option value="">All Languages</option>
            {languages.length > 0 ? (
              languages.map((lang) => (
                <option key={lang.code} value={lang.code}>
                  {lang.name} ({lang.code})
                </option>
              ))
            ) : (
              <>
                <option value="en-US">English (US)</option>
                <option value="en-GB">English (UK)</option>
                <option value="es-ES">Spanish (ES)</option>
                <option value="fr-FR">French (FR)</option>
                <option value="de-DE">German (DE)</option>
                <option value="hi-IN">Hindi (IN)</option>
              </>
            )}
          </select>
        </div>

        {hasActiveFilters && (
          <button
            onClick={resetFilters}
            className="flex items-center space-x-1 px-3 py-2 text-xs text-slate-400 hover:text-bloop-400 transition"
          >
            <RotateCcw className="w-3 h-3" aria-hidden="true" />
            <span>Reset</span>
          </button>
        )}
      </div>

      {/* Error state */}
      {isError && (
        <div className="mb-8 p-4 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <AlertTriangle className="w-5 h-5 shrink-0 text-rose-400" aria-hidden="true" />
            <span>{(error as Error)?.message || 'We could not load your favorites.'}</span>
          </div>
          <button
            onClick={() => refetch()}
            className="px-3 py-1.5 rounded-xl bg-rose-500/20 hover:bg-rose-500/30 text-white font-medium text-xs transition"
          >
            Try Again
          </button>
        </div>
      )}

      {/* Favorites Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-48 rounded-2xl bg-slate-800/40 border border-white/5" />
          ))}
        </div>
      ) : favorites.length === 0 ? (
        <div className="glass-panel rounded-2xl p-12 text-center border border-white/10 flex flex-col items-center justify-center gap-3">
          <div className="w-14 h-14 rounded-full bg-slate-800 flex items-center justify-center text-amber-400/40">
            <Star className="w-6 h-6" aria-hidden="true" />
          </div>
          <p className="text-base font-semibold text-white">
            {hasActiveFilters ? 'No matching favorites found' : 'No favorites bookmarked yet'}
          </p>
          <p className="text-xs text-slate-400 max-w-sm">
            {hasActiveFilters
              ? 'Try clearing your search query or language filter.'
              : 'Click the star icon on any speech generation in your History or Workspace to bookmark it here for instant access.'}
          </p>
          {hasActiveFilters ? (
            <button
              onClick={resetFilters}
              className="mt-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold transition"
            >
              Reset Filters
            </button>
          ) : (
            <div className="flex items-center space-x-3 mt-2">
              <Link
                to="/workspace"
                className="px-4 py-2 rounded-xl bg-bloop-600 hover:bg-bloop-500 text-white text-xs font-semibold shadow-md transition"
              >
                Create Speech
              </Link>
              <Link
                to="/history"
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-white/10 text-xs font-semibold transition"
              >
                Browse History
              </Link>
            </div>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {favorites.map((fav) => {
            if (!fav.generation) return null;
            return (
              <GenerationCard
                key={fav.id}
                generation={{
                  ...fav.generation,
                  is_favorite: true,
                  favorite_id: fav.id,
                }}
                onToggleFavorite={() => removeFavoriteMutation.mutate(fav.id)}
                onDelete={(id) => deleteGenerationMutation.mutate(id)}
                onViewDetail={(g) => setSelectedGen(g)}
              />
            );
          })}
        </div>
      )}

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <nav className="flex items-center justify-center space-x-3 mt-10" aria-label="Favorites Pagination">
          <button
            onClick={() => setPage((p) => Math.max(p - 1, 1))}
            disabled={page === 1}
            aria-label="Go to previous page"
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-white border border-white/10 transition"
          >
            <ChevronLeft className="w-5 h-5" aria-hidden="true" />
          </button>
          <span className="text-sm font-medium text-slate-300">
            Page <span className="font-bold text-white">{page}</span> of {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(p + 1, totalPages))}
            disabled={page === totalPages}
            aria-label="Go to next page"
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-white border border-white/10 transition"
          >
            <ChevronRight className="w-5 h-5" aria-hidden="true" />
          </button>
        </nav>
      )}

      {/* Generation Detail Modal */}
      <GenerationDetailModal
        isOpen={Boolean(selectedGen)}
        onClose={() => setSelectedGen(null)}
        generation={selectedGen}
        onToggleFavorite={(g) => {
          if (g.favorite_id) {
            removeFavoriteMutation.mutate(g.favorite_id);
          }
          setSelectedGen(null);
        }}
        onDelete={(id) => {
          deleteGenerationMutation.mutate(id);
          setSelectedGen(null);
        }}
      />
    </div>
  );
};
