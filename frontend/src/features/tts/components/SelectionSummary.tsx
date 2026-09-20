import React from 'react';
import { CheckCircle2, AlertCircle, Globe, Mic } from 'lucide-react';
import { Language, Voice } from '../../../types';
import { Badge } from '../../../components/ui';

export interface SelectionSummaryProps {
  language?: Language | null;
  voice?: Voice | null;
  isCompatible: boolean;
}

export const SelectionSummary: React.FC<SelectionSummaryProps> = ({
  language,
  voice,
  isCompatible,
}) => {
  if (!language && !voice) {
    return null;
  }

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-xl bg-slate-900/60 border border-white/5 text-xs">
      <div className="flex flex-wrap items-center gap-3">
        {/* Language Badge */}
        {language ? (
          <div className="flex items-center space-x-1.5 text-slate-300">
            <Globe className="w-3.5 h-3.5 text-bloop-400" aria-hidden="true" />
            <span className="text-slate-400">Language:</span>
            <span className="font-medium text-white">{language.name}</span>
            <Badge variant="indigo" className="text-[10px]">
              {language.code}
            </Badge>
          </div>
        ) : (
          <span className="text-slate-500 italic">No language selected</span>
        )}

        <span className="text-slate-700 hidden sm:inline">•</span>

        {/* Voice Badge */}
        {voice ? (
          <div className="flex items-center space-x-1.5 text-slate-300">
            <Mic className="w-3.5 h-3.5 text-bloop-400" aria-hidden="true" />
            <span className="text-slate-400">Voice:</span>
            <span className="font-medium text-white">{voice.name}</span>
            <Badge variant="slate" className="text-[10px]">
              {voice.gender}
            </Badge>
            {voice.is_user_configured && (
              <Badge variant="amber" className="text-[10px]">
                Custom
              </Badge>
            )}
          </div>
        ) : (
          <span className="text-slate-500 italic">No voice selected</span>
        )}
      </div>

      {/* Compatibility Status */}
      {language && voice && (
        <div className="flex items-center space-x-1">
          {isCompatible ? (
            <span className="flex items-center space-x-1 text-emerald-400 text-[11px] font-medium">
              <CheckCircle2 className="w-3.5 h-3.5" aria-hidden="true" />
              <span>Compatible</span>
            </span>
          ) : (
            <span className="flex items-center space-x-1 text-rose-400 text-[11px] font-medium">
              <AlertCircle className="w-3.5 h-3.5" aria-hidden="true" />
              <span>Incompatible</span>
            </span>
          )}
        </div>
      )}
    </div>
  );
};
