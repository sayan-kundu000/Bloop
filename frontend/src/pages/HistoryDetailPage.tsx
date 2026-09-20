import React from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  ArrowLeft,
  FileText,
  Clock,
  Globe,
  Mic,
  Trash2,
  Star,
  Copy,
  Check,
  Loader2,
  AlertCircle,
  Edit3,
  ChevronRight,
} from 'lucide-react';
import { historyApi, ttsApi } from '../api/client';
import { useWorkspaceStore } from '../stores/workspaceStore';
import { AudioPlayer } from '../features/audio';
import { AudioSource } from '../features/audio/types/audio.types';

export const HistoryDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [copied, setCopied] = React.useState(false);

  const generationId = Number(id);

  const { data: generation, isLoading, isError, error } = useQuery({
    queryKey: ['generation-detail', generationId],
    queryFn: () => historyApi.getGeneration(generationId),
    enabled: !isNaN(generationId) && generationId > 0,
    staleTime: 1000 * 60,
  });

  const toggleFavoriteMutation = useMutation({
    mutationFn: async () => {
      if (!generation) return;
      if (generation.is_favorite && generation.favorite_id) {
        await historyApi.removeFavorite(generation.favorite_id);
      } else {
        await historyApi.addFavorite(generation.id);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['generation-detail', generationId] });
      queryClient.invalidateQueries({ queryKey: ['history'] });
      queryClient.invalidateQueries({ queryKey: ['favorites'] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => historyApi.deleteGeneration(generationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['history'] });
      queryClient.invalidateQueries({ queryKey: ['favorites'] });
      navigate('/history');
    },
  });

  const handleUseAsNew = () => {
    if (!generation) return;
    // Load historical text, language, and voice into workspace store
    useWorkspaceStore.getState().setText(generation.text);
    if (generation.language_code) {
      useWorkspaceStore.getState().setLanguageCode(generation.language_code);
    }
    if (generation.voice_id) {
      useWorkspaceStore.getState().setVoiceId(generation.voice_id);
    }
    navigate('/workspace');
  };

  const handleCopyText = () => {
    if (!generation) return;
    navigator.clipboard.writeText(generation.text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const formatDate = (isoStr: string) => {
    try {
      return new Date(isoStr).toLocaleString(undefined, {
        dateStyle: 'medium',
        timeStyle: 'medium',
      });
    } catch {
      return isoStr;
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center flex flex-col items-center justify-center gap-3">
        <Loader2 className="w-8 h-8 text-bloop-400 animate-spin" aria-hidden="true" />
        <p className="text-sm text-slate-400">Loading generation record #{id}...</p>
      </div>
    );
  }

  if (isError || !generation) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-6">
        <button
          onClick={() => navigate('/history')}
          className="flex items-center space-x-1.5 text-xs text-slate-400 hover:text-white transition"
        >
          <ArrowLeft className="w-4 h-4" aria-hidden="true" />
          <span>Back to Speech History</span>
        </button>

        <div className="glass-panel rounded-2xl p-8 border border-white/10 text-center flex flex-col items-center justify-center gap-3">
          <AlertCircle className="w-10 h-10 text-rose-400" aria-hidden="true" />
          <h2 className="text-lg font-bold text-white">Generation Record Not Found</h2>
          <p className="text-xs text-slate-400 max-w-md">
            {(error as Error)?.message || 'This speech generation record is no longer available or you do not have permission to view it.'}
          </p>
          <button
            onClick={() => navigate('/history')}
            className="mt-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold transition"
          >
            Return to Speech History
          </button>
        </div>
      </div>
    );
  }

  // Construct normalized AudioSource for Prompt 20 AudioPlayer
  const audioSource: AudioSource = {
    audioUrl: ttsApi.getAudioUrl(generation.audio_url),
    downloadUrl: ttsApi.getAudioUrl(generation.download_url),
    title: generation.voice_name || `Speech #${generation.id}`,
    voiceName: generation.voice_name,
    duration: generation.duration_seconds,
    text: generation.text,
    generationId: generation.id,
    audioFormat: 'mp3',
    contentType: 'audio/mpeg',
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6 animate-fade-in">
      {/* Breadcrumb Navigation (Prompt 21 §52) */}
      <nav className="flex items-center space-x-2 text-xs text-slate-400" aria-label="Breadcrumb">
        <Link to="/history" className="hover:text-white transition flex items-center space-x-1">
          <ArrowLeft className="w-3.5 h-3.5" aria-hidden="true" />
          <span>Speech History</span>
        </Link>
        <ChevronRight className="w-3.5 h-3.5 text-slate-600" aria-hidden="true" />
        <span className="text-slate-200 font-medium">Generation #{generation.id}</span>
      </nav>

      {/* Main Generation Inspection Container */}
      <div className="glass-panel rounded-2xl border border-white/10 shadow-xl overflow-hidden">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between px-6 py-5 border-b border-white/10 gap-4">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-bloop-600/20 text-bloop-400">
              <FileText className="w-6 h-6" aria-hidden="true" />
            </div>
            <div>
              <h1 className="text-xl font-extrabold text-white">Speech Generation #{generation.id}</h1>
              <span className="text-xs text-slate-400 flex items-center space-x-1 mt-0.5">
                <Clock className="w-3 h-3" aria-hidden="true" />
                <span>{formatDate(generation.created_at)}</span>
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {/* Use as New Draft in Workspace */}
            <button
              onClick={handleUseAsNew}
              className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-xs font-semibold transition"
              title="Load text into Create Speech workspace"
            >
              <Edit3 className="w-3.5 h-3.5" aria-hidden="true" />
              <span>Use as New</span>
            </button>

            {/* Favorite Toggle */}
            <button
              onClick={() => toggleFavoriteMutation.mutate()}
              className={`flex items-center space-x-1 px-3 py-2 rounded-xl text-xs font-medium border transition ${
                generation.is_favorite
                  ? 'bg-amber-500/10 border-amber-500/30 text-amber-400'
                  : 'bg-slate-800 border-white/10 text-slate-300 hover:text-amber-400'
              }`}
            >
              <Star className={`w-3.5 h-3.5 ${generation.is_favorite ? 'fill-amber-400' : ''}`} aria-hidden="true" />
              <span>{generation.is_favorite ? 'Bookmarked' : 'Favorite'}</span>
            </button>

            {/* Delete Record */}
            <button
              onClick={() => {
                if (window.confirm('Are you sure you want to delete this speech generation record? This action cannot be undone.')) {
                  deleteMutation.mutate();
                }
              }}
              className="flex items-center space-x-1 px-3 py-2 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20 text-xs font-medium transition"
              title="Delete this record"
            >
              <Trash2 className="w-3.5 h-3.5" aria-hidden="true" />
              <span>Delete</span>
            </button>
          </div>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-6">
          {/* Spoken Text Section (Safe Plain-Text Rendering) */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Synthesized Text Content
              </span>
              <button
                onClick={handleCopyText}
                className="flex items-center space-x-1 text-xs text-bloop-400 hover:text-bloop-300 transition"
              >
                {copied ? <Check className="w-3.5 h-3.5" aria-hidden="true" /> : <Copy className="w-3.5 h-3.5" aria-hidden="true" />}
                <span>{copied ? 'Copied' : 'Copy Text'}</span>
              </button>
            </div>
            <div className="p-5 rounded-xl bg-slate-900/90 border border-white/10 text-sm text-slate-100 leading-relaxed font-sans whitespace-pre-wrap select-text break-words">
              {generation.text}
            </div>
          </div>

          {/* Prompt 20 Integrated AudioPlayer (Prompt 21 §30, §67) */}
          <div className="pt-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 block mb-2">
              Audio Playback & Media Delivery
            </span>
            <AudioPlayer source={audioSource} />
          </div>

          {/* Quick Metrics */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-4 rounded-xl bg-slate-900/70 border border-white/5">
              <span className="text-xs text-slate-400 block mb-1">Language</span>
              <span className="text-sm font-bold text-white flex items-center space-x-1">
                <Globe className="w-4 h-4 text-bloop-400" aria-hidden="true" />
                <span>{generation.language_code}</span>
              </span>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/70 border border-white/5">
              <span className="text-xs text-slate-400 block mb-1">Voice ID</span>
              <span className="text-sm font-bold text-white truncate flex items-center space-x-1" title={generation.voice_id}>
                <Mic className="w-4 h-4 text-quantum-400" aria-hidden="true" />
                <span className="truncate">{generation.voice_name || generation.voice_id}</span>
              </span>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/70 border border-white/5">
              <span className="text-xs text-slate-400 block mb-1">Audio Duration</span>
              <span className="text-sm font-bold text-white flex items-center space-x-1">
                <Clock className="w-4 h-4 text-emerald-400" aria-hidden="true" />
                <span>{generation.duration_seconds}s</span>
              </span>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/70 border border-white/5">
              <span className="text-xs text-slate-400 block mb-1">Generation Status</span>
              <span className={`text-sm font-bold capitalize ${generation.status === 'completed' ? 'text-emerald-400' : 'text-rose-400'}`}>
                {generation.status}
              </span>
            </div>
          </div>

          {/* Technical Metadata */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            <div className="p-3.5 rounded-xl bg-slate-900/50 border border-white/5 flex justify-between">
              <span className="text-slate-400">Total Character Count:</span>
              <span className="font-mono text-white">{generation.char_count} chars</span>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-900/50 border border-white/5 flex justify-between">
              <span className="text-slate-400">Total Word Count:</span>
              <span className="font-mono text-white">{generation.word_count} words</span>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-900/50 border border-white/5 flex justify-between">
              <span className="text-slate-400">Audio File Size:</span>
              <span className="font-mono text-white">{(generation.file_size_bytes / 1024).toFixed(1)} KB</span>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-900/50 border border-white/5 flex justify-between">
              <span className="text-slate-400">TTS Provider:</span>
              <span className="font-mono uppercase text-quantum-300">{generation.provider}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
