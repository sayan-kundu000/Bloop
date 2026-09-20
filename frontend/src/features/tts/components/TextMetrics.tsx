import React from 'react';
import { Hash, Clock, AlertTriangle } from 'lucide-react';
import { TextMetricsData } from '../types/tts.types';

export interface TextMetricsProps {
  metrics: TextMetricsData;
}

export const TextMetrics: React.FC<TextMetricsProps> = ({ metrics }) => {
  const {
    characterCount,
    wordCount,
    estimatedDurationSeconds,
    maxCharacters,
    isNearLimit,
    isAtLimit,
    isOverLimit,
    percentageUsed,
  } = metrics;

  // Visual status for character count
  const statusColorClass = isOverLimit
    ? 'text-rose-400 font-bold'
    : isAtLimit || isNearLimit
    ? 'text-amber-400 font-semibold'
    : 'text-slate-200';

  const progressBgClass = isOverLimit
    ? 'bg-rose-500'
    : isNearLimit || isAtLimit
    ? 'bg-amber-500'
    : 'bg-bloop-500';

  return (
    <div
      id="text-metrics-bar"
      className="flex flex-wrap items-center justify-between gap-3 text-xs pt-2"
      aria-label="Text statistics"
    >
      {/* Counters */}
      <div className="flex items-center space-x-4 text-slate-400 font-medium">
        {/* Character count */}
        <span className="flex items-center space-x-1.5" title="Character count">
          <Hash className="w-3.5 h-3.5 text-bloop-400" aria-hidden="true" />
          <span>Characters:</span>
          <span className={statusColorClass}>{characterCount.toLocaleString()}</span>
          <span>/</span>
          <span>{maxCharacters.toLocaleString()}</span>
        </span>

        {/* Word count */}
        <span className="flex items-center space-x-1" title="Word count">
          <span>Words:</span>
          <span className="text-slate-200 font-bold">{wordCount.toLocaleString()}</span>
        </span>

        {/* Estimated duration */}
        <span className="hidden sm:flex items-center space-x-1 text-slate-400" title="Estimated audio duration">
          <Clock className="w-3.5 h-3.5 text-quantum-400" aria-hidden="true" />
          <span>~{estimatedDurationSeconds}s audio</span>
        </span>
      </div>

      {/* Progress meter */}
      <div className="flex items-center space-x-2">
        {(isNearLimit || isOverLimit) && (
          <span className="flex items-center space-x-1 text-[11px] font-medium text-amber-400">
            <AlertTriangle className="w-3 h-3" aria-hidden="true" />
            <span>{isOverLimit ? 'Over limit' : 'Near limit'}</span>
          </span>
        )}
        <div
          className="w-24 sm:w-32 bg-slate-800/80 rounded-full h-2 overflow-hidden border border-white/5"
          role="progressbar"
          aria-valuenow={characterCount}
          aria-valuemin={0}
          aria-valuemax={maxCharacters}
          aria-label="Character limit progress"
        >
          <div
            className={`h-full transition-all duration-150 ${progressBgClass}`}
            style={{ width: `${Math.min(percentageUsed, 100)}%` }}
          />
        </div>
      </div>
    </div>
  );
};
