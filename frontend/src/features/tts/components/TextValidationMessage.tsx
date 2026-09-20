import React from 'react';
import { AlertCircle, AlertTriangle } from 'lucide-react';
import { WorkspaceValidationResult } from '../types/tts.types';

export interface TextValidationMessageProps {
  validation: WorkspaceValidationResult;
}

export const TextValidationMessage: React.FC<TextValidationMessageProps> = ({ validation }) => {
  const { error, code, isOverLimit } = validation;

  if (!error) {
    return null;
  }

  // Choose styling depending on severity: over limit or mismatch is an error; empty text is a helpful prompt
  const isSevere = isOverLimit || code === 'VOICE_LANGUAGE_MISMATCH' || code === 'TEXT_TOO_LONG';

  return (
    <div
      role="alert"
      className={`flex items-start space-x-2.5 p-3 rounded-xl text-xs font-medium border transition-all ${
        isSevere
          ? 'bg-rose-950/30 border-rose-800/60 text-rose-300'
          : 'bg-amber-950/20 border-amber-800/40 text-amber-300'
      }`}
    >
      {isSevere ? (
        <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" aria-hidden="true" />
      ) : (
        <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" aria-hidden="true" />
      )}
      <div className="flex-1">
        <p>{error}</p>
      </div>
    </div>
  );
};
