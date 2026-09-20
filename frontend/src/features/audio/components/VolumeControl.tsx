import React from 'react';
import { Volume2, Volume1, VolumeX } from 'lucide-react';

export interface VolumeControlProps {
  volume: number; // 0.0 to 1.0
  isMuted: boolean;
  onVolumeChange: (vol: number) => void;
  onToggleMute: () => void;
  disabled?: boolean;
  className?: string;
}

export const VolumeControl: React.FC<VolumeControlProps> = ({
  volume,
  isMuted,
  onVolumeChange,
  onToggleMute,
  disabled = false,
  className = '',
}) => {
  const effectiveVolume = isMuted ? 0 : volume;

  const renderVolumeIcon = () => {
    if (isMuted || effectiveVolume === 0) {
      return <VolumeX className="w-4 h-4 text-slate-400" aria-hidden="true" />;
    }
    if (effectiveVolume < 0.5) {
      return <Volume1 className="w-4 h-4 text-slate-300" aria-hidden="true" />;
    }
    return <Volume2 className="w-4 h-4 text-bloop-400" aria-hidden="true" />;
  };

  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      {/* Mute / Unmute Button */}
      <button
        type="button"
        onClick={onToggleMute}
        disabled={disabled}
        aria-label={isMuted ? 'Unmute audio' : 'Mute audio'}
        title={isMuted ? 'Unmute' : 'Mute'}
        className="p-2 rounded-lg bg-slate-900/60 hover:bg-slate-800 text-slate-400 hover:text-white border border-white/5 transition disabled:opacity-40 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-bloop-500/50"
      >
        {renderVolumeIcon()}
      </button>

      {/* Volume Slider */}
      <div className="relative flex items-center w-20 sm:w-24 group">
        <input
          type="range"
          min={0}
          max={1}
          step={0.05}
          value={effectiveVolume}
          disabled={disabled}
          onChange={(e) => onVolumeChange(parseFloat(e.target.value))}
          aria-label="Adjust volume"
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={Math.round(effectiveVolume * 100)}
          aria-valuetext={`${Math.round(effectiveVolume * 100)} percent volume`}
          className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-bloop-400 disabled:cursor-not-allowed focus:outline-none"
        />
      </div>
    </div>
  );
};
