import React from 'react';
import { CheckCircle2, Volume2, Clock, Sparkles, AlertTriangle, FileAudio } from 'lucide-react';
import { TTSResponse } from '../../../types';

import { AudioPlayer } from '../../audio';

export interface GenerationSuccessProps {
  result: TTSResponse | null;
  currentText?: string;
  onPlay?: (url: string, title: string) => void;
  className?: string;
}

export const GenerationSuccess: React.FC<GenerationSuccessProps> = ({
  result,
  currentText,
  onPlay,
  className = '',
}) => {
  if (!result) return null;

  // Check if current editor text has diverged from synthesized text
  const isTextDiverged =
    typeof currentText === 'string' &&
    currentText.trim() !== '' &&
    currentText.trim() !== result.text.trim();

  return (
    <div
      role="region"
      aria-label="Generation result"
      className={`p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/30 text-emerald-200 text-sm shadow-lg space-y-3 animate-fade-in ${className}`}
    >
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-emerald-500/20 pb-2.5">
        <div className="flex items-center space-x-2">
          <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" aria-hidden="true" />
          <span className="font-semibold text-emerald-100">Speech generated successfully.</span>
        </div>

        <div className="flex items-center space-x-2">
          {result.is_simulation && (
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30 font-mono">
              Simulation Mode
            </span>
          )}
          <span className="text-xs font-mono text-emerald-300/80 bg-emerald-900/30 px-2.5 py-0.5 rounded-lg border border-emerald-700/40">
            {(result.audio_format || 'mp3').toUpperCase()}
          </span>
        </div>
      </div>

      {/* Text Divergence Warning */}
      {isTextDiverged && (
        <div className="flex items-center space-x-2 p-2.5 rounded-lg bg-amber-950/40 border border-amber-500/30 text-amber-300 text-xs">
          <AlertTriangle className="w-4 h-4 shrink-0 text-amber-400" aria-hidden="true" />
          <span>
            The workspace text has changed since this audio was synthesized. Click <strong>Generate Speech</strong> to synthesize with your new text.
          </span>
        </div>
      )}

      {/* Metadata summary */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
        <div className="p-2 rounded-lg bg-slate-900/60 border border-white/5">
          <span className="text-slate-400 block text-[10px] uppercase tracking-wider">Voice</span>
          <span className="font-semibold text-white truncate block">
            {result.voice_name || result.voice_id}
          </span>
        </div>

        <div className="p-2 rounded-lg bg-slate-900/60 border border-white/5">
          <span className="text-slate-400 block text-[10px] uppercase tracking-wider">Duration</span>
          <span className="font-semibold text-white block flex items-center space-x-1">
            <Clock className="w-3 h-3 text-slate-400 inline" aria-hidden="true" />
            <span>~{result.duration_seconds}s</span>
          </span>
        </div>

        <div className="p-2 rounded-lg bg-slate-900/60 border border-white/5">
          <span className="text-slate-400 block text-[10px] uppercase tracking-wider">Length</span>
          <span className="font-semibold text-white block">
            {result.char_count} chars ({result.word_count} words)
          </span>
        </div>

        <div className="p-2 rounded-lg bg-slate-900/60 border border-white/5">
          <span className="text-slate-400 block text-[10px] uppercase tracking-wider">Locale</span>
          <span className="font-semibold text-white block">{result.language}</span>
        </div>
      </div>

      {/* Integrated Prompt 20 Bloop Audio Player */}
      <div
        id="tts-audio-handoff-container"
        data-generation-id={result.generation_id}
        data-audio-url={result.audio_url}
        className="pt-1"
      >
        <AudioPlayer result={result} currentText={currentText} />
      </div>
    </div>
  );
};
