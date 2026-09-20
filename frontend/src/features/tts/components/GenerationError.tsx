import React from 'react';
import { AlertCircle, X } from 'lucide-react';
import { RetryGenerationButton } from './RetryGenerationButton';

export interface GenerationErrorProps {
  error: string | null;
  isRetryable?: boolean;
  onRetry?: () => void;
  onDismiss?: () => void;
  isGenerating?: boolean;
  canRetry?: boolean;
  className?: string;
}

export const GenerationError: React.FC<GenerationErrorProps> = ({
  error,
  isRetryable = false,
  onRetry,
  onDismiss,
  isGenerating = false,
  canRetry = true,
  className = '',
}) => {
  if (!error) return null;

  return (
    <div
      role="alert"
      aria-live="assertive"
      className={`p-4 rounded-xl bg-rose-950/30 border border-rose-500/40 text-rose-200 text-sm shadow-lg flex flex-col sm:flex-row sm:items-center justify-between gap-3 animate-fade-in ${className}`}
    >
      <div className="flex items-start space-x-3">
        <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" aria-hidden="true" />
        <div className="space-y-1">
          <p className="font-semibold text-rose-100">Speech Generation Failed</p>
          <p className="text-xs text-rose-300 leading-relaxed">{error}</p>
        </div>
      </div>

      <div className="flex items-center space-x-2 self-end sm:self-center shrink-0">
        {isRetryable && onRetry && (
          <RetryGenerationButton
            onRetry={onRetry}
            disabled={!canRetry}
            isGenerating={isGenerating}
          />
        )}
        {onDismiss && (
          <button
            type="button"
            onClick={onDismiss}
            aria-label="Dismiss error"
            className="p-1 rounded-lg text-rose-300/70 hover:text-rose-100 hover:bg-rose-900/30 transition"
          >
            <X className="w-4 h-4" aria-hidden="true" />
          </button>
        )}
      </div>
    </div>
  );
};
