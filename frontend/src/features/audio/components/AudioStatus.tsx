import React from 'react';
import { Loader2, AlertTriangle, RefreshCw } from 'lucide-react';
import { AudioPlayerError, AudioPlayerStatus } from '../types/audio.types';

export interface AudioStatusProps {
  status: AudioPlayerStatus;
  isLoading: boolean;
  isBuffering: boolean;
  error: AudioPlayerError | null;
  audioFormat?: string;
  onRetry?: () => void;
  className?: string;
}

export const AudioStatus: React.FC<AudioStatusProps> = ({
  status,
  isLoading,
  isBuffering,
  error,
  audioFormat,
  onRetry,
  className = '',
}) => {
  if (error) {
    return (
      <div
        role="alert"
        className={`flex items-center justify-between p-3 rounded-xl bg-rose-950/40 border border-rose-500/30 text-rose-200 text-xs shadow-inner animate-fade-in ${className}`}
      >
        <div className="flex items-center space-x-2.5">
          <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" aria-hidden="true" />
          <span>{error.message}</span>
        </div>

        {error.retryable && onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="flex items-center space-x-1 px-2.5 py-1 rounded-lg bg-rose-900/60 hover:bg-rose-800 text-rose-100 font-medium border border-rose-700/50 transition focus:outline-none focus:ring-2 focus:ring-rose-400"
          >
            <RefreshCw className="w-3 h-3" aria-hidden="true" />
            <span>Retry</span>
          </button>
        )}
      </div>
    );
  }

  if (isLoading || isBuffering) {
    return (
      <div
        role="status"
        aria-live="polite"
        className={`flex items-center space-x-2 text-xs text-slate-400 animate-pulse ${className}`}
      >
        <Loader2 className="w-3.5 h-3.5 animate-spin text-bloop-400" aria-hidden="true" />
        <span>{isLoading ? 'Loading audio…' : 'Buffering audio…'}</span>
      </div>
    );
  }

  return (
    <div className={`flex items-center space-x-2 text-xs text-slate-500 ${className}`}>
      {audioFormat && (
        <span className="font-mono text-[10px] uppercase px-2 py-0.5 rounded bg-slate-900 border border-white/5 text-slate-400">
          {audioFormat}
        </span>
      )}
    </div>
  );
};
