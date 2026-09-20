import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Play, Pause, Star, Download, Trash2, Clock, Globe, Mic, Eye, Edit3 } from 'lucide-react';
import { SpeechGeneration } from '../../types';
import { useAudioStore } from '../../stores/audioStore';
import { useWorkspaceStore } from '../../stores/workspaceStore';
import { ttsApi } from '../../api/client';

interface GenerationCardProps {
  generation: SpeechGeneration;
  onToggleFavorite?: (gen: SpeechGeneration) => void;
  onDelete?: (id: number) => void;
  onViewDetail?: (gen: SpeechGeneration) => void;
  compact?: boolean;
}

export const GenerationCard: React.FC<GenerationCardProps> = ({
  generation,
  onToggleFavorite,
  onDelete,
  onViewDetail,
  compact = false,
}) => {
  const navigate = useNavigate();
  const { currentAudioUrl, isPlaying, playAudio, togglePlay } = useAudioStore();

  const fullAudioUrl = ttsApi.getAudioUrl(generation.audio_url);
  const isCurrent = currentAudioUrl === fullAudioUrl;

  const handlePlayClick = () => {
    if (isCurrent) {
      togglePlay();
    } else {
      playAudio(fullAudioUrl, generation.voice_name || `Speech #${generation.id}`);
    }
  };

  const handleUseAsNew = () => {
    // Populate workspace store with historical generation's parameters without modifying historical record
    useWorkspaceStore.getState().setText(generation.text);
    if (generation.language_code) {
      useWorkspaceStore.getState().setLanguageCode(generation.language_code);
    }
    if (generation.voice_id) {
      useWorkspaceStore.getState().setVoiceId(generation.voice_id);
    }
    navigate('/workspace');
  };

  const formatDate = (isoStr: string) => {
    try {
      const d = new Date(isoStr);
      return d.toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return isoStr;
    }
  };

  const downloadUrl = ttsApi.getAudioUrl(generation.download_url);

  return (
    <div className={`glass-panel glass-panel-hover rounded-2xl p-5 border border-white/10 flex flex-col justify-between gap-3.5 group ${compact ? 'py-4' : ''}`}>
      {/* Top Meta info */}
      <div className="flex items-center justify-between text-xs text-slate-400 border-b border-white/5 pb-2.5">
        <div className="flex items-center space-x-2">
          <span className="flex items-center space-x-1 px-2 py-0.5 rounded bg-slate-800 border border-white/5" title="Language code">
            <Globe className="w-3 h-3 text-bloop-400" aria-hidden="true" />
            <span>{generation.language_code}</span>
          </span>
          <span className="flex items-center space-x-1 px-2 py-0.5 rounded bg-slate-800 border border-white/5 max-w-[140px] truncate" title={generation.voice_name || generation.voice_id}>
            <Mic className="w-3 h-3 text-quantum-400 shrink-0" aria-hidden="true" />
            <span className="truncate">{generation.voice_name || generation.voice_id}</span>
          </span>
          {generation.provider && !compact && (
            <span className="text-[10px] px-1.5 py-0.5 rounded uppercase font-mono bg-white/5 text-slate-400">
              {generation.provider}
            </span>
          )}
        </div>

        <span className="flex items-center space-x-1 text-slate-500 text-[11px]">
          <Clock className="w-3 h-3" aria-hidden="true" />
          <span>{formatDate(generation.created_at)}</span>
        </span>
      </div>

      {/* Spoken Text (Plain Text Safe Rendering) */}
      <div className="flex-1">
        <p className="text-slate-100 text-sm leading-relaxed line-clamp-3 font-sans break-words select-text">
          &ldquo;{generation.text}&rdquo;
        </p>
      </div>

      {/* Footer: Stats, Playback & Actions */}
      <div className="flex items-center justify-between pt-2 border-t border-white/5">
        <div className="flex items-center space-x-2 text-[11px] text-slate-400">
          <span>{generation.char_count} chars</span>
          <span>•</span>
          <span>~{generation.duration_seconds}s</span>
        </div>

        <div className="flex items-center space-x-1">
          {/* Use as New Draft in Workspace */}
          <button
            onClick={handleUseAsNew}
            title="Load text into Create Speech workspace"
            aria-label={`Use generation ${generation.id} text as new draft in workspace`}
            className="p-1.5 rounded-lg text-slate-400 hover:text-emerald-400 hover:bg-emerald-500/10 transition"
          >
            <Edit3 className="w-4 h-4" aria-hidden="true" />
          </button>

          {/* View Details */}
          {onViewDetail ? (
            <button
              onClick={() => onViewDetail(generation)}
              title="Inspect metadata and generation details"
              aria-label={`Inspect details for generation ${generation.id}`}
              className="p-1.5 rounded-lg text-slate-400 hover:text-bloop-400 hover:bg-white/5 transition"
            >
              <Eye className="w-4 h-4" aria-hidden="true" />
            </button>
          ) : (
            <Link
              to={`/history/${generation.id}`}
              title="Inspect metadata and generation details"
              aria-label={`Inspect details for generation ${generation.id}`}
              className="p-1.5 rounded-lg text-slate-400 hover:text-bloop-400 hover:bg-white/5 transition"
            >
              <Eye className="w-4 h-4" aria-hidden="true" />
            </Link>
          )}

          {/* Favorite Toggle */}
          {onToggleFavorite && (
            <button
              onClick={() => onToggleFavorite(generation)}
              title={generation.is_favorite ? 'Remove from Favorites' : 'Add to Starred Favorites'}
              aria-label={generation.is_favorite ? `Remove generation ${generation.id} from favorites` : `Add generation ${generation.id} to favorites`}
              className={`p-1.5 rounded-lg transition ${
                generation.is_favorite
                  ? 'text-amber-400 bg-amber-400/10 hover:bg-amber-400/20'
                  : 'text-slate-400 hover:text-amber-400 hover:bg-white/5'
              }`}
            >
              <Star className={`w-4 h-4 ${generation.is_favorite ? 'fill-amber-400' : ''}`} aria-hidden="true" />
            </button>
          )}

          {/* Download Audio */}
          <a
            href={downloadUrl}
            download
            title="Download Audio File"
            aria-label={`Download audio file for generation ${generation.id}`}
            className="p-1.5 rounded-lg text-slate-400 hover:text-bloop-400 hover:bg-bloop-500/10 transition"
          >
            <Download className="w-4 h-4" aria-hidden="true" />
          </a>

          {/* Delete Record */}
          {onDelete && (
            <button
              onClick={() => onDelete(generation.id)}
              title="Delete speech record"
              aria-label={`Delete generation ${generation.id}`}
              className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition"
            >
              <Trash2 className="w-4 h-4" aria-hidden="true" />
            </button>
          )}

          {/* Play/Pause Button */}
          <button
            onClick={handlePlayClick}
            aria-label={isCurrent && isPlaying ? `Pause generation ${generation.id}` : `Play generation ${generation.id}`}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold shadow-md transition ml-1 ${
              isCurrent && isPlaying
                ? 'bg-amber-500 hover:bg-amber-400 text-black shadow-amber-500/20'
                : 'bg-bloop-600 hover:bg-bloop-500 text-white shadow-bloop-600/30'
            }`}
          >
            {isCurrent && isPlaying ? (
              <>
                <Pause className="w-3.5 h-3.5" aria-hidden="true" />
                <span>Pause</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current" aria-hidden="true" />
                <span>Play</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

