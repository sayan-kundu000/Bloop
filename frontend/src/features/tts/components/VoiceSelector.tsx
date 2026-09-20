import React, { useMemo } from 'react';
import { Mic, RefreshCw, AlertCircle, Sparkles } from 'lucide-react';
import { Voice } from '../../../types';
import { Skeleton } from '../../../components/ui';
import { isVoiceCompatibleWithLanguage } from '../utils/textValidation';

export interface VoiceSelectorProps {
  voices: Voice[];
  selectedVoiceId: string | null;
  selectedLanguageCode: string | null;
  onSelectVoice: (voiceId: string) => void;
  isLoading?: boolean;
  isError?: boolean;
  onRetry?: () => void;
  disabled?: boolean;
}

export const VoiceSelector: React.FC<VoiceSelectorProps> = ({
  voices,
  selectedVoiceId,
  selectedLanguageCode,
  onSelectVoice,
  isLoading = false,
  isError = false,
  onRetry,
  disabled = false,
}) => {
  // Filter voices compatible with selected language locale
  const compatibleVoices = useMemo(() => {
    if (!selectedLanguageCode) {
      return voices;
    }
    return voices.filter((v) => isVoiceCompatibleWithLanguage(v, selectedLanguageCode));
  }, [voices, selectedLanguageCode]);

  return (
    <div className="flex flex-col space-y-1.5 w-full">
      {/* Label */}
      <label
        htmlFor="tts-voice-select"
        className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center justify-between"
      >
        <span className="flex items-center space-x-1.5">
          <Mic className="w-3.5 h-3.5 text-bloop-400" aria-hidden="true" />
          <span>Speech Voice</span>
        </span>
        {compatibleVoices.length > 0 && !isLoading && (
          <span className="text-[11px] text-slate-500 font-mono">
            {compatibleVoices.length} compatible
          </span>
        )}
      </label>

      {/* Loading Skeleton */}
      {isLoading ? (
        <div className="w-full h-10 bg-slate-900/80 rounded-xl border border-white/5 p-2 flex items-center">
          <Skeleton className="w-full h-5" rounded="md" />
        </div>
      ) : isError ? (
        /* Error State with Retry */
        <div className="flex items-center justify-between p-2.5 bg-rose-950/20 border border-rose-800/40 rounded-xl text-xs text-rose-300">
          <div className="flex items-center space-x-1.5">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" aria-hidden="true" />
            <span>Unable to load voices.</span>
          </div>
          {onRetry && (
            <button
              type="button"
              onClick={onRetry}
              className="px-2 py-1 bg-rose-900/40 hover:bg-rose-800/60 rounded text-rose-200 text-xs font-medium flex items-center space-x-1 transition"
            >
              <RefreshCw className="w-3 h-3" aria-hidden="true" />
              <span>Retry</span>
            </button>
          )}
        </div>
      ) : compatibleVoices.length === 0 ? (
        /* Empty State */
        <div className="p-2.5 bg-slate-900/60 border border-slate-800 rounded-xl text-xs text-slate-400 text-center">
          {selectedLanguageCode
            ? `No voices available for language '${selectedLanguageCode}'.`
            : 'No voices available in catalog.'}
        </div>
      ) : (
        /* Loaded Native Select */
        <div className="relative">
          <select
            id="tts-voice-select"
            name="voiceId"
            value={selectedVoiceId || ''}
            onChange={(e) => onSelectVoice(e.target.value)}
            disabled={disabled}
            className="w-full bg-slate-900/90 text-slate-100 text-sm rounded-xl px-3.5 py-2.5 border border-white/10 focus:outline-none focus:border-bloop-500 focus:ring-2 focus:ring-bloop-500/30 appearance-none cursor-pointer pr-10 hover:border-white/20 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <option value="" disabled className="bg-slate-900 text-slate-500">
              -- Select Voice --
            </option>
            {compatibleVoices.map((voice) => {
              const genderTag = voice.gender ? ` (${voice.gender})` : '';
              const accentTag = voice.accent ? ` • ${voice.accent}` : '';
              const customTag = voice.is_user_configured ? ' ★ Custom' : '';
              return (
                <option key={voice.voice_id} value={voice.voice_id} className="bg-slate-900 text-white">
                  {voice.name}
                  {genderTag}
                  {accentTag}
                  {customTag}
                </option>
              );
            })}
          </select>
          <div className="pointer-events-none absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 text-xs" aria-hidden="true">
            ▼
          </div>
        </div>
      )}
    </div>
  );
};
