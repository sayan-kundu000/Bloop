import React from 'react';
import { Loader2, Sparkles, Volume2 } from 'lucide-react';

export interface GenerationStatusProps {
  isGenerating: boolean;
  voiceName?: string | null;
  languageCode?: string | null;
  className?: string;
}

/**
 * GenerationStatus Component
 * Displays indeterminate progress feedback during speech synthesis.
 * Invariant: Never displays fake percentages (e.g. "47% complete").
 * Meets accessible status live-region standards (role="status", aria-live="polite").
 */
export const GenerationStatus: React.FC<GenerationStatusProps> = ({
  isGenerating,
  voiceName,
  languageCode,
  className = '',
}) => {
  if (!isGenerating) {
    return null;
  }

  return (
    <div
      role="status"
      aria-live="polite"
      aria-busy="true"
      className={`p-4 rounded-xl bg-bloop-950/40 border border-bloop-500/30 text-slate-200 text-sm shadow-lg flex flex-col sm:flex-row sm:items-center justify-between gap-3 animate-fade-in ${className}`}
    >
      <div className="flex items-center space-x-3">
        <div className="w-8 h-8 rounded-lg bg-bloop-500/20 border border-bloop-500/40 flex items-center justify-center shrink-0">
          <Loader2 className="w-4 h-4 text-bloop-400 animate-spin" aria-hidden="true" />
        </div>
        <div>
          <p className="font-semibold text-white flex items-center space-x-1.5">
            <span>Generating speech…</span>
            <Sparkles className="w-3.5 h-3.5 text-bloop-400 animate-pulse" aria-hidden="true" />
          </p>
          <p className="text-xs text-slate-400 mt-0.5">
            Synthesizing natural voice with dynamic provider backend
            {voiceName ? ` (${voiceName})` : ''}
            {languageCode ? ` [${languageCode}]` : ''}.
          </p>
        </div>
      </div>

      <div className="flex items-center space-x-2 text-xs font-mono text-bloop-300/80 bg-slate-900/60 px-3 py-1.5 rounded-lg border border-white/5 self-start sm:self-center">
        <span className="w-2 h-2 rounded-full bg-bloop-400 animate-ping shrink-0" aria-hidden="true" />
        <span>Processing request</span>
      </div>
    </div>
  );
};
