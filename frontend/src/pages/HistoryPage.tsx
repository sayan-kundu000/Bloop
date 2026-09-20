import React, { useState, useEffect, useMemo } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  History as HistoryIcon,
  Search,
  Globe,
  ChevronLeft,
  ChevronRight,
  RefreshCw,
  SlidersHorizontal,
  Activity,
  Star,
  Calendar,
  X,
  AlertTriangle,
  RotateCcw,
} from 'lucide-react';
import { voiceApi } from '../api/client';
import { useSpeechHistory, useToggleFavoriteMutation, useDeleteGenerationMutation } from '../features/history';
import { GenerationCard } from '../components/tts/GenerationCard';
import { GenerationDetailModal } from '../components/tts/GenerationDetailModal';
import { SpeechGeneration } from '../types';

export const HistoryPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  // Read initial states from URL query parameters (Prompt 16 §44 & Prompt 21 §23)
  const initialSearch = searchParams.get('search') || '';
  const initialLang = searchParams.get('language') || '';
  const initialStatus = searchParams.get('status') || '';
  const initialFavorite = searchParams.get('favorite') === 'true';
  const initialSort = searchParams.get('sort') || 'newest';
  const initialDateRange = searchParams.get('date_range') || 'all';
  const initialPage = parseInt(searchParams.get('page') || '1', 10) || 1;

  const [searchTerm, setSearchTerm] = useState(initialSearch);
  const [debouncedSearch, setDebouncedSearch] = useState(initialSearch);
  const [selectedLang, setSelectedLang] = useState(initialLang);
  const [selectedStatus, setSelectedStatus] = useState(initialStatus);
  const [favoriteOnly, setFavoriteOnly] = useState(initialFavorite);
  const [sortOption, setSortOption] = useState(initialSort);
  const [dateRange, setDateRange] = useState(initialDateRange);
  const [page, setPage] = useState(initialPage);

  // Detail Modal state
  const [selectedGen, setSelectedGen] = useState<SpeechGeneration | null>(null);

  // Dynamic Languages catalogue (Prompt 21 §114)
  const { data: languages = [] } = useQuery({
    queryKey: ['languages'],
    queryFn: () => voiceApi.getLanguages(),
    staleTime: 1000 * 60 * 10,
  });

  // Debounce search input (300ms) (Prompt 21 §22)
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(searchTerm.trim());
      setPage(1);
    }, 300);
    return () => clearTimeout(handler);
  }, [searchTerm]);

  // Derive sort parameters from sortOption allowlist
  const { sortBy, sortOrder } = useMemo(() => {
    switch (sortOption) {
      case 'oldest':
        return { sortBy: 'created_at', sortOrder: 'asc' };
      case 'duration_desc':
        return { sortBy: 'duration_seconds', sortOrder: 'desc' };
      case 'char_count_desc':
        return { sortBy: 'char_count', sortOrder: 'desc' };
      case 'newest':
      default:
        return { sortBy: 'created_at', sortOrder: 'desc' };
    }
  }, [sortOption]);

  // Derive ISO created_after timestamp from dateRange preset
  const createdAfter = useMemo(() => {
    const now = new Date();
    if (dateRange === 'today') {
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      return today.toISOString();
    }
    if (dateRange === '7d') {
      const past = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      return past.toISOString();
    }
    if (dateRange === '30d') {
      const past = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
      return past.toISOString();
    }
    return undefined;
  }, [dateRange]);

  // Sync state changes to URL query parameters
  useEffect(() => {
    const params: Record<string, string> = {};
    if (debouncedSearch) params.search = debouncedSearch;
    if (selectedLang) params.language = selectedLang;
    if (selectedStatus) params.status = selectedStatus;
    if (favoriteOnly) params.favorite = 'true';
    if (sortOption !== 'newest') params.sort = sortOption;
    if (dateRange !== 'all') params.date_range = dateRange;
    if (page > 1) params.page = page.toString();

    setSearchParams(params, { replace: true });
  }, [debouncedSearch, selectedLang, selectedStatus, favoriteOnly, sortOption, dateRange, page, setSearchParams]);

  // Query hook using features/history abstraction
  const { data, isLoading, refetch, isFetching, isError, error } = useSpeechHistory({
    search: debouncedSearch || undefined,
    language: selectedLang || undefined,
    status: selectedStatus || undefined,
    favorite: favoriteOnly ? true : undefined,
    created_after: createdAfter,
    sort_by: sortBy,
    order: sortOrder,
    page,
    page_size: 12,
  });

  // Favorite & Delete mutations
  const toggleFavoriteMutation = useToggleFavoriteMutation();
  const deleteMutation = useDeleteGenerationMutation();

  const items = data?.items || [];
  const total = data?.total || 0;
  const totalPages = Math.ceil(total / 12) || 1;

  const hasActiveFilters = Boolean(
    searchTerm || selectedLang || selectedStatus || favoriteOnly || dateRange !== 'all'
  );

  const resetFilters = () => {
    setSearchTerm('');
    setDebouncedSearch('');
    setSelectedLang('');
    setSelectedStatus('');
    setFavoriteOnly(false);
    setDateRange('all');
    setSortOption('newest');
    setPage(1);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center space-x-3">
            <HistoryIcon className="w-8 h-8 text-bloop-400" aria-hidden="true" />
            <span>Speech Generation <span className="gradient-text-bloop">History</span></span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Search, filter, organize, bookmark, and inspect metadata for all synthesized speech generations.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <Link
            to="/favorites"
            className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 text-xs font-semibold transition"
          >
            <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" aria-hidden="true" />
            <span>View Favorites</span>
          </Link>

          <button
            onClick={() => refetch()}
            disabled={isFetching}
            className="flex items-center space-x-2 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-white/10 text-xs font-medium transition disabled:opacity-50"
            title="Refresh history records"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isFetching ? 'animate-spin' : ''}`} aria-hidden="true" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Search, Filters & Sorting Bar (Prompt 21 §20-27) */}
      <div className="glass-panel rounded-2xl p-4 border border-white/10 mb-8 flex flex-col gap-3">
        <div className="flex flex-col lg:flex-row items-stretch lg:items-center gap-3">
          {/* Debounced Search Input */}
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" aria-hidden="true" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search spoken text or voice name..."
              aria-label="Search speech history"
              className="w-full bg-slate-900/90 text-xs text-white rounded-xl pl-10 pr-10 py-2.5 border border-white/10 focus:outline-none focus:border-bloop-500 transition"
            />
            {searchTerm && (
              <button
                onClick={() => setSearchTerm('')}
                aria-label="Clear search input"
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
              >
                <X className="w-3.5 h-3.5" aria-hidden="true" />
              </button>
            )}
          </div>

          {/* Dynamic Language Filter (Prompt 21 §114) */}
          <div className="flex items-center space-x-2">
            <Globe className="w-4 h-4 text-slate-400 shrink-0" aria-hidden="true" />
            <select
              value={selectedLang}
              onChange={(e) => {
                setSelectedLang(e.target.value);
                setPage(1);
              }}
              aria-label="Filter by language"
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

          {/* Status Filter */}
          <div className="flex items-center space-x-2">
            <Activity className="w-4 h-4 text-slate-400 shrink-0" aria-hidden="true" />
            <select
              value={selectedStatus}
              onChange={(e) => {
                setSelectedStatus(e.target.value);
                setPage(1);
              }}
              aria-label="Filter by generation status"
              className="bg-slate-900/90 text-xs text-white rounded-xl px-3 py-2.5 border border-white/10 focus:outline-none focus:border-bloop-500 cursor-pointer min-w-28"
            >
              <option value="">All Statuses</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
              <option value="pending">Pending</option>
              <option value="processing">Processing</option>
            </select>
          </div>

          {/* Date Range Preset Filter */}
          <div className="flex items-center space-x-2">
            <Calendar className="w-4 h-4 text-slate-400 shrink-0" aria-hidden="true" />
            <select
              value={dateRange}
              onChange={(e) => {
                setDateRange(e.target.value);
                setPage(1);
              }}
              aria-label="Filter by date range"
              className="bg-slate-900/90 text-xs text-white rounded-xl px-3 py-2.5 border border-white/10 focus:outline-none focus:border-bloop-500 cursor-pointer min-w-28"
            >
              <option value="all">All Time</option>
              <option value="today">Today</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
            </select>
          </div>

          {/* Sort Allowlist Dropdown (Prompt 21 §26) */}
          <div className="flex items-center space-x-2">
            <SlidersHorizontal className="w-4 h-4 text-slate-400 shrink-0" aria-hidden="true" />
            <select
              value={sortOption}
              onChange={(e) => {
                setSortOption(e.target.value);
                setPage(1);
              }}
              aria-label="Sort speech history"
              className="bg-slate-900/90 text-xs text-white rounded-xl px-3 py-2.5 border border-white/10 focus:outline-none focus:border-bloop-500 cursor-pointer min-w-36"
            >
              <option value="newest">Newest First</option>
              <option value="oldest">Oldest First</option>
              <option value="duration_desc">Longest Duration</option>
              <option value="char_count_desc">Most Characters</option>
            </select>
          </div>
        </div>

        {/* Secondary Filter Row: Favorites Only & Active Filter Badges */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-white/5 text-xs">
          <div className="flex items-center space-x-3">
            {/* Favorites Only Toggle */}
            <button
              onClick={() => {
                setFavoriteOnly((prev) => !prev);
                setPage(1);
              }}
              aria-pressed={favoriteOnly}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-xl font-medium border transition ${
                favoriteOnly
                  ? 'bg-amber-400/20 text-amber-300 border-amber-400/40 shadow-sm'
                  : 'bg-slate-800/80 text-slate-400 border-white/5 hover:text-slate-200'
              }`}
            >
              <Star className={`w-3.5 h-3.5 ${favoriteOnly ? 'fill-amber-400 text-amber-400' : 'text-slate-400'}`} aria-hidden="true" />
              <span>Favorites Only</span>
            </button>

            {/* Total Results Counter (Prompt 21 §110 & §112) */}
            <span className="text-slate-400">
              Showing <span className="font-semibold text-white">{items.length}</span> of <span className="font-semibold text-white">{total}</span> records
            </span>
          </div>

          {/* Reset Filters action */}
          {hasActiveFilters && (
            <button
              onClick={resetFilters}
              className="flex items-center space-x-1 text-slate-400 hover:text-bloop-400 transition"
            >
              <RotateCcw className="w-3 h-3" aria-hidden="true" />
              <span>Reset Filters</span>
            </button>
          )}
        </div>
      </div>

      {/* Error state */}
      {isError && (
        <div className="mb-8 p-4 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <AlertTriangle className="w-5 h-5 shrink-0 text-rose-400" aria-hidden="true" />
            <span>{(error as Error)?.message || 'We could not load your speech history.'}</span>
          </div>
          <button
            onClick={() => refetch()}
            className="px-3 py-1.5 rounded-xl bg-rose-500/20 hover:bg-rose-500/30 text-white font-medium text-xs transition"
          >
            Try Again
          </button>
        </div>
      )}

      {/* Generation Cards Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="h-48 rounded-2xl bg-slate-800/40 border border-white/5" />
          ))}
        </div>
      ) : items.length === 0 ? (
        <div className="glass-panel rounded-2xl p-12 text-center border border-white/10 flex flex-col items-center justify-center gap-3">
          <div className="w-14 h-14 rounded-full bg-slate-800 flex items-center justify-center text-slate-500">
            <HistoryIcon className="w-6 h-6" aria-hidden="true" />
          </div>
          <p className="text-base font-semibold text-white">No speech generations found</p>
          <p className="text-xs text-slate-400 max-w-sm">
            {hasActiveFilters
              ? 'Try clearing your search query or loosening your filter criteria.'
              : 'Synthesize your first text in the Create Speech workspace to start building your speech history.'}
          </p>
          {hasActiveFilters ? (
            <button
              onClick={resetFilters}
              className="mt-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold transition"
            >
              Clear All Filters
            </button>
          ) : (
            <Link
              to="/workspace"
              className="mt-2 px-4 py-2 rounded-xl bg-bloop-600 hover:bg-bloop-500 text-white text-xs font-semibold shadow-md transition"
            >
              Create Speech
            </Link>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {items.map((gen) => (
            <GenerationCard
              key={gen.id}
              generation={gen}
              onToggleFavorite={(g) => toggleFavoriteMutation.mutate(g)}
              onDelete={(id) => deleteMutation.mutate(id)}
              onViewDetail={(g) => setSelectedGen(g)}
            />
          ))}
        </div>
      )}

      {/* Pagination Controls (Prompt 21 §18 & §19) */}
      {totalPages > 1 && (
        <nav className="flex items-center justify-center space-x-3 mt-10" aria-label="History Pagination">
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

      {/* Deep Inspection Detail Modal */}
      <GenerationDetailModal
        isOpen={Boolean(selectedGen)}
        onClose={() => setSelectedGen(null)}
        generation={selectedGen}
        onToggleFavorite={(g) => {
          toggleFavoriteMutation.mutate(g);
          setSelectedGen((prev) => (prev ? { ...prev, is_favorite: !prev.is_favorite } : null));
        }}
        onDelete={(id) => {
          deleteMutation.mutate(id);
          setSelectedGen(null);
        }}
      />
    </div>
  );
};
