import React from 'react';
import { GenerateButton } from './GenerateButton';
import { GenerationStatus } from './GenerationStatus';
import { GenerationError } from './GenerationError';
import { GenerationSuccess } from './GenerationSuccess';
import { TTSResponse } from '../../../types';

export interface GenerationControlsProps {
  canGenerate: boolean;
  isGenerating: boolean;
  onGenerate: () => void;
  isError: boolean;
  errorMessage: string | null;
  isRetryable: boolean;
  onRetry: () => void;
  onDismissError?: () => void;
  result: TTSResponse | null;
  currentText?: string;
  voiceName?: string | null;
  languageCode?: string | null;
  onPlayResult?: (url: string, title: string) => void;
  readinessHint?: string | null;
  className?: string;
}

/**
 * GenerationControls Component
 * Orchestrates the speech synthesis lifecycle: readiness validation, action triggering,
 * indeterminate loading feedback, error alerting with retry, and success results handoff.
 */
export const GenerationControls: React.FC<GenerationControlsProps> = ({
  canGenerate,
  isGenerating,
  onGenerate,
  isError,
  errorMessage,
  isRetryable,
  onRetry,
  onDismissError,
  result,
  currentText,
  voiceName,
  languageCode,
  onPlayResult,
  readinessHint,
  className = '',
}) => {
  return (
    <div className={`space-y-4 pt-3 border-t border-white/10 ${className}`}>
      {/* 1. Indeterminate Loading Feedback */}
      <GenerationStatus
        isGenerating={isGenerating}
        voiceName={voiceName}
        languageCode={languageCode}
      />

      {/* 2. Error Feedback with Retry Action */}
      {isError && (
        <GenerationError
          error={errorMessage}
          isRetryable={isRetryable}
          onRetry={onRetry}
          onDismiss={onDismissError}
          isGenerating={isGenerating}
          canRetry={canGenerate}
        />
      )}

      {/* 3. Generation Success & Metadata Handoff */}
      {result && !isGenerating && (
        <GenerationSuccess
          result={result}
          currentText={currentText}
          onPlay={onPlayResult}
        />
      )}

      {/* 4. Action Row: Readiness Note + Generate Button */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="text-xs text-slate-400 w-full sm:w-auto">
          {readinessHint ? (
            <span>{readinessHint}</span>
          ) : canGenerate ? (
            <span className="text-emerald-400 font-medium">Ready to synthesize speech</span>
          ) : (
            <span>Complete required inputs to enable synthesis.</span>
          )}
        </div>

        <GenerateButton
          onClick={onGenerate}
          isGenerating={isGenerating}
          disabled={!canGenerate}
          className="w-full sm:w-auto"
        />
      </div>
    </div>
  );
};
