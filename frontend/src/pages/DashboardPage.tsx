import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  LayoutDashboard,
  Volume2,
  Mic,
  Star,
  ArrowRight,
  Sparkles,
  RefreshCw,
  AlertCircle,
  Clock,
  Atom,
  History as HistoryIcon,
  PlusCircle,
} from 'lucide-react';
import { historyApi, voiceApi, quantumApi } from '../api/client';
import { useAuthStore } from '../stores/authStore';
import { GenerationCard } from '../components/tts/GenerationCard';
import { GenerationDetailModal } from '../components/tts/GenerationDetailModal';
import { useToggleFavoriteMutation, useDeleteGenerationMutation } from '../features/history';
import { SpeechGeneration } from '../types';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [selectedGen, setSelectedGen] = useState<SpeechGeneration | null>(null);

  // Recent speech generations query (limit 4 for focused dashboard overview)
  const {
    data: recentHistoryData,
    isLoading: isHistoryLoading,
    isError: isHistoryError,
    error: historyError,
    refetch: refetchHistory,
    isFetching: isHistoryFetching,
  } = useQuery({
    queryKey: ['history', { page: 1, page_size: 4 }],
    queryFn: () => historyApi.getHistory({ page: 1, page_size: 4 }),
    staleTime: 1000 * 30,
  });

  // Favorite generations preview query (limit 4)
  const {
    data: favoritesData,
    isLoading: isFavoritesLoading,
    isError: isFavoritesError,
    refetch: refetchFavorites,
  } = useQuery({
    queryKey: ['favorites', { page: 1, page_size: 4 }],
    queryFn: () => historyApi.getFavorites({ page: 1, page_size: 4 }),
    staleTime: 1000 * 30,
  });

  // Dynamic voices catalogue count
  const { data: voices = [] } = useQuery({
    queryKey: ['voices'],
    queryFn: () => voiceApi.getVoices(),
    staleTime: 1000 * 60 * 5,
  });

  // Decoupled quantum experiment count (isolated, dashboard does not break if quantum fails)
  const { data: quantumExperiments = [] } = useQuery({
    queryKey: ['quantum_history'],
    queryFn: async () => {
      try {
        return await quantumApi.getHistory();
      } catch {
        return [];
      }
    },
    staleTime: 1000 * 60 * 5,
    retry: false,
  });

  const toggleFavoriteMutation = useToggleFavoriteMutation();
  const deleteMutation = useDeleteGenerationMutation();

  const recentItems = recentHistoryData?.items || [];
  const totalGenerations = recentHistoryData?.total ?? 0;
  const favoriteItems: SpeechGeneration[] = (favoritesData?.items || []).flatMap((fav) =>
    fav.generation ? [{ ...fav.generation, is_favorite: true, favorite_id: fav.id }] : []
  );
  const totalFavorites = favoritesData?.total ?? 0;

  const handleRefreshAll = () => {
    refetchHistory();
    refetchFavorites();
  };

  const userName = user?.full_name || user?.email?.split('@')[0] || 'Creator';

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-fade-in">
      {/* 1. Welcome & Workspace Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/10 pb-6">
        <div>
          <div className="flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-bloop-400 mb-1">
            <Sparkles className="w-3.5 h-3.5" aria-hidden="true" />
            <span>Authenticated Creator Workspace</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            Welcome back, <span className="gradient-text-bloop font-['Outfit']">{userName}</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1 max-w-2xl">
            Synthesize high-fidelity natural speech, manage your voice generations, and access your starred favorites.
          </p>
        </div>

        <div className="flex items-center space-x-3 shrink-0">
          <button
            onClick={handleRefreshAll}
            disabled={isHistoryFetching}
            className="flex items-center space-x-1.5 px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-white/10 text-xs font-medium transition disabled:opacity-50"
            title="Refresh dashboard data"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isHistoryFetching ? 'animate-spin' : ''}`} aria-hidden="true" />
            <span>Refresh</span>
          </button>

          <Link
            to="/workspace"
            className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-bloop-600 hover:bg-bloop-500 text-white text-xs font-bold shadow-lg shadow-bloop-600/30 transition hover:scale-[1.02]"
          >
            <PlusCircle className="w-4 h-4" aria-hidden="true" />
            <span>Create Speech</span>
          </Link>
        </div>
      </div>

      {/* 2. Overview Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Speech Generations */}
        <Link
          to="/history"
          className="glass-panel glass-panel-hover rounded-2xl p-5 border border-white/10 flex items-center justify-between group transition-all"
        >
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Generations</p>
            <p className="text-2xl font-black text-white mt-1 group-hover:text-bloop-300 transition">
              {totalGenerations}
            </p>
            <p className="text-[11px] text-slate-500 mt-0.5 flex items-center space-x-1">
              <span>View full audit log</span>
              <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" aria-hidden="true" />
            </p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-bloop-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-bloop-600/20 text-white">
            <Volume2 className="w-6 h-6" aria-hidden="true" />
          </div>
        </Link>

        {/* Starred Favorites */}
        <Link
          to="/favorites"
          className="glass-panel glass-panel-hover rounded-2xl p-5 border border-white/10 flex items-center justify-between group transition-all"
        >
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Starred Favorites</p>
            <p className="text-2xl font-black text-white mt-1 group-hover:text-amber-300 transition">
              {totalFavorites}
            </p>
            <p className="text-[11px] text-slate-500 mt-0.5 flex items-center space-x-1">
              <span>View bookmarked audio</span>
              <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" aria-hidden="true" />
            </p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-amber-500 to-orange-600 flex items-center justify-center shadow-lg shadow-amber-500/20 text-white">
            <Star className="w-6 h-6 fill-white" aria-hidden="true" />
          </div>
        </Link>

        {/* Dynamic Voices */}
        <Link
          to="/workspace"
          className="glass-panel glass-panel-hover rounded-2xl p-5 border border-white/10 flex items-center justify-between group transition-all"
        >
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Dynamic Voices</p>
            <p className="text-2xl font-black text-white mt-1 group-hover:text-quantum-300 transition">
              {voices.length}
            </p>
            <p className="text-[11px] text-slate-500 mt-0.5 flex items-center space-x-1">
              <span>Ready in Studio</span>
              <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" aria-hidden="true" />
            </p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-quantum-600 to-purple-600 flex items-center justify-center shadow-lg shadow-quantum-600/20 text-white">
            <Mic className="w-6 h-6" aria-hidden="true" />
          </div>
        </Link>

        {/* Quantum Intelligence Engine (Isolated) */}
        <Link
          to="/quantum"
          className="glass-panel glass-panel-hover rounded-2xl p-5 border border-white/10 flex items-center justify-between group transition-all"
        >
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Quantum Lab</p>
            <p className="text-2xl font-black text-white mt-1 group-hover:text-pink-300 transition">
              {quantumExperiments.length}
            </p>
            <p className="text-[11px] text-slate-500 mt-0.5 flex items-center space-x-1">
              <span>Circuits & QNNs</span>
              <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" aria-hidden="true" />
            </p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-purple-600 to-pink-600 flex items-center justify-center shadow-lg shadow-purple-600/20 text-white">
            <Atom className="w-6 h-6" aria-hidden="true" />
          </div>
        </Link>
      </div>

      {/* 3. Main Dashboard Grid: Recent Generations (Left) + Favorites & Quick Access (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column (7 cols): Recent Generations */}
        <div className="lg:col-span-7 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Clock className="w-5 h-5 text-bloop-400" aria-hidden="true" />
              <h2 className="text-lg font-bold text-white">Recent Generations</h2>
            </div>
            {totalGenerations > 0 && (
              <Link
                to="/history"
                className="text-xs font-semibold text-bloop-400 hover:text-bloop-300 flex items-center space-x-1 transition"
              >
                <span>View all ({totalGenerations})</span>
                <ArrowRight className="w-3.5 h-3.5" aria-hidden="true" />
              </Link>
            )}
          </div>

          {/* Error State */}
          {isHistoryError && (
            <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" aria-hidden="true" />
                <span>{(historyError as Error)?.message || 'Unable to load recent history.'}</span>
              </div>
              <button
                onClick={() => refetchHistory()}
                className="px-2.5 py-1 rounded bg-rose-500/20 hover:bg-rose-500/30 text-white font-medium"
              >
                Try Again
              </button>
            </div>
          )}

          {/* Loading Skeletons */}
          {isHistoryLoading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-28 rounded-2xl bg-slate-800/40 border border-white/5 animate-pulse" />
              ))}
            </div>
          ) : recentItems.length === 0 ? (
            /* Empty State */
            <div className="glass-panel rounded-2xl p-8 text-center border border-white/10 flex flex-col items-center justify-center space-y-3">
              <div className="w-12 h-12 rounded-2xl bg-slate-800 flex items-center justify-center text-slate-500">
                <HistoryIcon className="w-6 h-6" aria-hidden="true" />
              </div>
              <p className="text-sm font-semibold text-white">No speech generations yet</p>
              <p className="text-xs text-slate-400 max-w-sm">
                Transform any written thought into high-definition synthesized speech using our dynamic neural voices.
              </p>
              <Link
                to="/workspace"
                className="mt-2 px-4 py-2 rounded-xl bg-bloop-600 hover:bg-bloop-500 text-white text-xs font-semibold shadow-md transition"
              >
                Create Your First Speech
              </Link>
            </div>
          ) : (
            /* Generation Cards List */
            <div className="space-y-3.5">
              {recentItems.map((gen) => (
                <GenerationCard
                  key={gen.id}
                  generation={gen}
                  compact
                  onToggleFavorite={(g) => toggleFavoriteMutation.mutate(g)}
                  onDelete={(id) => deleteMutation.mutate(id)}
                  onViewDetail={(g) => setSelectedGen(g)}
                />
              ))}
            </div>
          )}
        </div>

        {/* Right Column (5 cols): Starred Favorites Preview & Quick Action Launchpad */}
        <div className="lg:col-span-5 space-y-6">
          {/* Starred Favorites Section */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Star className="w-5 h-5 text-amber-400 fill-amber-400" aria-hidden="true" />
                <h2 className="text-lg font-bold text-white">Starred Favorites</h2>
              </div>
              {totalFavorites > 0 && (
                <Link
                  to="/favorites"
                  className="text-xs font-semibold text-amber-400 hover:text-amber-300 flex items-center space-x-1 transition"
                >
                  <span>View all ({totalFavorites})</span>
                  <ArrowRight className="w-3.5 h-3.5" aria-hidden="true" />
                </Link>
              )}
            </div>

            {isFavoritesLoading ? (
              <div className="space-y-3">
                {[1, 2].map((i) => (
                  <div key={i} className="h-28 rounded-2xl bg-slate-800/40 border border-white/5 animate-pulse" />
                ))}
              </div>
            ) : favoriteItems.length === 0 ? (
              <div className="glass-panel rounded-2xl p-6 text-center border border-white/10 flex flex-col items-center justify-center space-y-2">
                <div className="w-10 h-10 rounded-xl bg-slate-800/80 flex items-center justify-center text-amber-400/40">
                  <Star className="w-5 h-5" aria-hidden="true" />
                </div>
                <p className="text-xs font-semibold text-white">No bookmarked favorites yet</p>
                <p className="text-[11px] text-slate-400 max-w-xs">
                  Star any generation in your History or Workspace to keep quick access to high-priority audio here.
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {favoriteItems.map((gen) => (
                  <GenerationCard
                    key={gen.id}
                    generation={gen}
                    compact
                    onToggleFavorite={(g) => toggleFavoriteMutation.mutate(g)}
                    onDelete={(id) => deleteMutation.mutate(id)}
                    onViewDetail={(g) => setSelectedGen(g)}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Quick Launchpad Box */}
          <div className="glass-panel rounded-2xl p-5 border border-white/10 space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">Quick Navigation</h3>
            <div className="grid grid-cols-2 gap-2.5">
              <Link
                to="/workspace"
                className="p-3 rounded-xl bg-slate-900/80 hover:bg-bloop-900/20 border border-white/5 hover:border-bloop-500/40 transition flex flex-col justify-between group"
              >
                <Volume2 className="w-4 h-4 text-bloop-400 mb-1" aria-hidden="true" />
                <span className="text-xs font-semibold text-white group-hover:text-bloop-300">Create Speech</span>
              </Link>
              <Link
                to="/history"
                className="p-3 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-white/5 hover:border-white/20 transition flex flex-col justify-between group"
              >
                <HistoryIcon className="w-4 h-4 text-indigo-400 mb-1" aria-hidden="true" />
                <span className="text-xs font-semibold text-white group-hover:text-indigo-300">Browse History</span>
              </Link>
              <Link
                to="/favorites"
                className="p-3 rounded-xl bg-slate-900/80 hover:bg-amber-950/20 border border-white/5 hover:border-amber-500/40 transition flex flex-col justify-between group"
              >
                <Star className="w-4 h-4 text-amber-400 mb-1" aria-hidden="true" />
                <span className="text-xs font-semibold text-white group-hover:text-amber-300">Saved Audio</span>
              </Link>
              <Link
                to="/quantum"
                className="p-3 rounded-xl bg-slate-900/80 hover:bg-quantum-900/20 border border-white/5 hover:border-quantum-500/40 transition flex flex-col justify-between group"
              >
                <Atom className="w-4 h-4 text-quantum-400 mb-1" aria-hidden="true" />
                <span className="text-xs font-semibold text-white group-hover:text-quantum-300">Quantum Lab</span>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Generation Detail Modal for Deep Inspection from Dashboard */}
      <GenerationDetailModal
        isOpen={Boolean(selectedGen)}
        onClose={() => setSelectedGen(null)}
        generation={selectedGen}
        onToggleFavorite={(g) => toggleFavoriteMutation.mutate(g)}
        onDelete={(id) => deleteMutation.mutate(id)}
      />
    </div>
  );
};
