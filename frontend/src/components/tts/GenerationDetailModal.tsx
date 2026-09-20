import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  X,
  Play,
  Pause,
  Download,
  Trash2,
  Star,
  Copy,
  Check,
  Globe,
  Mic,
  Clock,
  FileText,
  Edit3,
} from 'lucide-react';
import { SpeechGeneration } from '../../types';
import { useAudioStore } from '../../stores/audioStore';
import { useWorkspaceStore } from '../../stores/workspaceStore';
import { ttsApi } from '../../api/client';

interface GenerationDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  generation: SpeechGeneration | null;
  onToggleFavorite?: (gen: SpeechGeneration) => void;
  onDelete?: (id: number) => void;
}

export const GenerationDetailModal: React.FC<GenerationDetailModalProps> = ({
  isOpen,
  onClose,
  generation,
  onToggleFavorite,
  onDelete,
}) => {
  const navigate = useNavigate();
  const [copied, setCopied] = React.useState(false);
  const { currentAudioUrl, isPlaying, playAudio, togglePlay } = useAudioStore();

  if (!isOpen || !generation) return null;

  const fullAudioUrl = ttsApi.getAudioUrl(generation.audio_url);
  const downloadUrl = ttsApi.getAudioUrl(generation.download_url);
  const isCurrent = currentAudioUrl === fullAudioUrl;

  const handlePlayClick = () => {
    if (isCurrent) {
      togglePlay();
    } else {
      playAudio(fullAudioUrl, generation.voice_name || `Speech #${generation.id}`);
    }
  };

  const handleUseAsNew = () => {
    useWorkspaceStore.getState().setText(generation.text);
    if (generation.language_code) {
      useWorkspaceStore.getState().setLanguageCode(generation.language_code);
    }
    if (generation.voice_id) {
      useWorkspaceStore.getState().setVoiceId(generation.voice_id);
    }
    onClose();
    navigate('/workspace');
  };

  const handleCopyText = () => {
    navigator.clipboard.writeText(generation.text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const formatDate = (isoStr: string) => {
    try {
      const d = new Date(isoStr);
      return d.toLocaleString(undefined, {
        dateStyle: 'medium',
        timeStyle: 'medium',
      });
    } catch {
      return isoStr;
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div
        className="glass-panel w-full max-w-2xl rounded-2xl border border-white/15 bg-slate-950/95 shadow-2xl overflow-hidden flex flex-col max-h-[90vh]"
        role="dialog"
        aria-modal="true"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/10">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-xl bg-bloop-600/20 text-bloop-400">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">Speech Generation #{generation.id}</h2>
              <span className="text-xs text-slate-400">{formatDate(generation.created_at)}</span>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-6">
          {/* Spoken Text Card */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Synthesized Text Content
              </span>
              <button
                onClick={handleCopyText}
                className="flex items-center space-x-1 text-xs text-bloop-400 hover:text-bloop-300 transition"
              >
                {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copied ? 'Copied' : 'Copy Text'}</span>
              </button>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/90 border border-white/10 text-sm text-slate-100 leading-relaxed max-h-48 overflow-y-auto font-sans whitespace-pre-wrap">
              {generation.text}
            </div>
          </div>

          {/* Key Metrics Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3 rounded-xl bg-slate-900/70 border border-white/5">
              <span className="text-[10px] uppercase font-semibold text-slate-400 block mb-0.5">Language</span>
              <span className="text-xs font-bold text-white flex items-center space-x-1">
                <Globe className="w-3 h-3 text-bloop-400" />
                <span>{generation.language_code}</span>
              </span>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/70 border border-white/5">
              <span className="text-[10px] uppercase font-semibold text-slate-400 block mb-0.5">Voice</span>
              <span className="text-xs font-bold text-white truncate flex items-center space-x-1" title={generation.voice_id}>
                <Mic className="w-3 h-3 text-quantum-400" />
                <span className="truncate">{generation.voice_name || generation.voice_id}</span>
              </span>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/70 border border-white/5">
              <span className="text-[10px] uppercase font-semibold text-slate-400 block mb-0.5">Duration</span>
              <span className="text-xs font-bold text-white flex items-center space-x-1">
                <Clock className="w-3 h-3 text-emerald-400" />
                <span>{generation.duration_seconds}s</span>
              </span>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/70 border border-white/5">
              <span className="text-[10px] uppercase font-semibold text-slate-400 block mb-0.5">Status</span>
              <span className={`text-xs font-bold capitalize ${generation.status === 'completed' ? 'text-emerald-400' : 'text-rose-400'}`}>
                {generation.status}
              </span>
            </div>
          </div>

          {/* Detailed Metadata Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            <div className="p-3 rounded-xl bg-slate-900/50 border border-white/5 flex justify-between">
              <span className="text-slate-400">Total Characters:</span>
              <span className="font-mono text-white">{generation.char_count}</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/50 border border-white/5 flex justify-between">
              <span className="text-slate-400">Total Words:</span>
              <span className="font-mono text-white">{generation.word_count}</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/50 border border-white/5 flex justify-between">
              <span className="text-slate-400">Audio File Size:</span>
              <span className="font-mono text-white">{(generation.file_size_bytes / 1024).toFixed(1)} KB</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/50 border border-white/5 flex justify-between">
              <span className="text-slate-400">TTS Provider:</span>
              <span className="font-mono uppercase text-quantum-300">{generation.provider}</span>
            </div>
          </div>
        </div>

        {/* Footer with Actions */}
        <div className="flex flex-wrap items-center justify-between px-6 py-4 border-t border-white/10 bg-slate-900/60 gap-3">
          <div className="flex items-center space-x-2">
            {/* Use as New */}
            <button
              onClick={handleUseAsNew}
              className="flex items-center space-x-1 px-3 py-2 rounded-xl bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-xs font-semibold transition"
              title="Load text into Create Speech workspace"
            >
              <Edit3 className="w-3.5 h-3.5" aria-hidden="true" />
              <span>Use as New</span>
            </button>

            {onDelete && (
              <button
                onClick={() => {
                  if (window.confirm('Are you sure you want to delete this speech generation record?')) {
                    onDelete(generation.id);
                    onClose();
                  }
                }}
                className="flex items-center space-x-1 px-3 py-2 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20 text-xs font-medium transition"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Delete</span>
              </button>
            )}

            {onToggleFavorite && (
              <button
                onClick={() => onToggleFavorite(generation)}
                className={`flex items-center space-x-1 px-3 py-2 rounded-xl text-xs font-medium border transition ${
                  generation.is_favorite
                    ? 'bg-amber-500/10 border-amber-500/30 text-amber-400'
                    : 'bg-slate-800 border-white/10 text-slate-300 hover:text-amber-400'
                }`}
              >
                <Star className={`w-3.5 h-3.5 ${generation.is_favorite ? 'fill-amber-400' : ''}`} />
                <span>{generation.is_favorite ? 'Bookmarked' : 'Favorite'}</span>
              </button>
            )}
          </div>

          <div className="flex items-center space-x-2">
            <a
              href={downloadUrl}
              download
              className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-white/10 text-xs font-medium transition"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download</span>
            </a>

            <button
              onClick={handlePlayClick}
              className={`flex items-center space-x-1.5 px-4 py-2 rounded-xl text-xs font-semibold shadow-md transition ${
                isCurrent && isPlaying
                  ? 'bg-amber-500 hover:bg-amber-400 text-black shadow-amber-500/20'
                  : 'bg-bloop-600 hover:bg-bloop-500 text-white shadow-bloop-600/30'
              }`}
            >
              {isCurrent && isPlaying ? (
                <>
                  <Pause className="w-3.5 h-3.5" />
                  <span>Pause</span>
                </>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>Play Audio</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
