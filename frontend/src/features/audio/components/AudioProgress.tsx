import React, { useCallback } from 'react';
import { formatDuration } from '../utils/audioUtils';

export interface AudioProgressProps {
  currentTime: number;
  duration: number;
  bufferedProgress?: number; // 0 to 100
  onSeek: (time: number) => void;
  disabled?: boolean;
  className?: string;
}

export const AudioProgress: React.FC<AudioProgressProps> = ({
  currentTime,
  duration,
  bufferedProgress = 0,
  onSeek,
  disabled = false,
  className = '',
}) => {
  const safeDuration = Math.max(0, duration || 0);
  const safeCurrent = Math.min(Math.max(0, currentTime || 0), safeDuration);
  const playPercent = safeDuration > 0 ? (safeCurrent / safeDuration) * 100 : 0;

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const val = parseFloat(e.target.value);
      if (!isNaN(val)) {
        onSeek(val);
      }
    },
    [onSeek]
  );

  return (
    <div className={`w-full flex items-center space-x-3 select-none ${className}`}>
      {/* Current Elapsed Time */}
      <span
        className="text-xs font-mono text-slate-400 w-11 text-right shrink-0"
        aria-hidden="true"
      >
        {formatDuration(safeCurrent)}
      </span>

      {/* Progress Track & Range Scrubber Container */}
      <div className="relative w-full flex items-center h-6 group">
        {/* Track Background */}
        <div className="absolute inset-x-0 h-1.5 rounded-full bg-slate-800 overflow-hidden pointer-events-none">
          {/* Buffered Fill */}
          <div
            className="h-full bg-slate-700/70 transition-all duration-300"
            style={{ width: `${Math.min(100, Math.max(0, bufferedProgress))}%` }}
          />
        </div>

        {/* Active Played Fill */}
        <div
          className="absolute left-0 h-1.5 rounded-full bg-gradient-to-r from-bloop-500 to-bloop-400 pointer-events-none transition-[width] duration-75"
          style={{ width: `${playPercent}%` }}
        />

        {/* Accessible Range Input */}
        <input
          type="range"
          min={0}
          max={safeDuration > 0 ? safeDuration : 0.1}
          step={0.1}
          value={safeCurrent}
          disabled={disabled || safeDuration === 0}
          onChange={handleChange}
          aria-label="Seek audio playback"
          aria-valuemin={0}
          aria-valuemax={Math.round(safeDuration)}
          aria-valuenow={Math.round(safeCurrent)}
          aria-valuetext={`${formatDuration(safeCurrent)} of ${formatDuration(safeDuration)}`}
          className="relative z-10 w-full h-4 opacity-0 cursor-pointer disabled:cursor-not-allowed group-hover:opacity-100 transition-opacity accent-bloop-400 focus:opacity-100 focus:outline-none"
        />

        {/* Playhead Thumb Indicator */}
        <div
          className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-3.5 h-3.5 rounded-full bg-white shadow-md shadow-black/50 border border-bloop-500 pointer-events-none transition-transform group-hover:scale-125"
          style={{ left: `${playPercent}%` }}
        />
      </div>

      {/* Total Duration */}
      <span
        className="text-xs font-mono text-slate-400 w-11 text-left shrink-0"
        aria-hidden="true"
      >
        {formatDuration(safeDuration)}
      </span>
    </div>
  );
};
