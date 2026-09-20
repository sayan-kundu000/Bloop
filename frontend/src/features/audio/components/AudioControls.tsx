import React from 'react';
import { Play, Pause, RotateCcw, RotateCw } from 'lucide-react';
import { AudioPlayerStatus } from '../types/audio.types';

export interface AudioControlsProps {
  status: AudioPlayerStatus;
  isPlaying: boolean;
  isEnded: boolean;
  isLoading: boolean;
  onTogglePlay: () => void;
  onRestart: () => void;
  onSeekRelative?: (deltaSeconds: number) => void;
  disabled?: boolean;
}

export const AudioControls: React.FC<AudioControlsProps> = ({
  status,
  isPlaying,
  isEnded,
  isLoading,
  onTogglePlay,
  onRestart,
  onSeekRelative,
  disabled = false,
}) => {
  const isActionDisabled = disabled || isLoading || status === 'error';

  return (
    <div className="flex items-center space-x-3" role="group" aria-label="Playback controls">
      {/* Rewind 5s */}
      {onSeekRelative && (
        <button
          type="button"
          onClick={() => onSeekRelative(-5)}
          disabled={isActionDisabled}
          aria-label="Rewind 5 seconds"
          title="Rewind 5 seconds"
          className="w-10 h-10 rounded-xl bg-slate-900/60 hover:bg-slate-800 text-slate-400 hover:text-slate-200 border border-white/5 flex items-center justify-center transition disabled:opacity-40 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-bloop-500/50"
        >
          <RotateCcw className="w-4 h-4" aria-hidden="true" />
        </button>
      )}

      {/* Main Play / Pause / Replay Button */}
      <button
        type="button"
        onClick={isEnded ? onRestart : onTogglePlay}
        disabled={isActionDisabled}
        aria-label={
          isEnded
            ? 'Replay generated speech'
            : isPlaying
            ? 'Pause generated speech'
            : 'Play generated speech'
        }
        title={
          isEnded
            ? 'Replay'
            : isPlaying
            ? 'Pause'
            : 'Play'
        }
        className={`w-12 h-12 rounded-2xl flex items-center justify-center font-semibold text-white shadow-lg transition transform active:scale-95 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-950 focus:ring-bloop-500 disabled:opacity-50 disabled:cursor-not-allowed ${
          isPlaying
            ? 'bg-amber-600 hover:bg-amber-500 shadow-amber-600/30'
            : 'bg-bloop-600 hover:bg-bloop-500 shadow-bloop-600/30'
        }`}
      >
        {isEnded ? (
          <RotateCcw className="w-5 h-5 text-white" aria-hidden="true" />
        ) : isPlaying ? (
          <Pause className="w-5 h-5 text-white fill-current" aria-hidden="true" />
        ) : (
          <Play className="w-5 h-5 text-white fill-current translate-x-0.5" aria-hidden="true" />
        )}
      </button>

      {/* Forward 5s */}
      {onSeekRelative && (
        <button
          type="button"
          onClick={() => onSeekRelative(5)}
          disabled={isActionDisabled}
          aria-label="Forward 5 seconds"
          title="Forward 5 seconds"
          className="w-10 h-10 rounded-xl bg-slate-900/60 hover:bg-slate-800 text-slate-400 hover:text-slate-200 border border-white/5 flex items-center justify-center transition disabled:opacity-40 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-bloop-500/50"
        >
          <RotateCw className="w-4 h-4" aria-hidden="true" />
        </button>
      )}
    </div>
  );
};
