import React from 'react';
import { RefreshCw } from 'lucide-react';

export interface RetryGenerationButtonProps {
  onRetry: () => void;
  disabled?: boolean;
  isGenerating?: boolean;
  className?: string;
  size?: 'sm' | 'md';
}

export const RetryGenerationButton: React.FC<RetryGenerationButtonProps> = ({
  onRetry,
  disabled = false,
  isGenerating = false,
  className = '',
  size = 'sm',
}) => {
  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    if (disabled || isGenerating) return;
    onRetry();
  };

  const isSmall = size === 'sm';

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={disabled || isGenerating}
      aria-label="Retry speech generation with current inputs"
      className={`rounded-lg font-medium flex items-center space-x-1.5 transition text-rose-200 bg-rose-900/40 hover:bg-rose-800/60 border border-rose-700/50 disabled:opacity-50 disabled:cursor-not-allowed ${
        isSmall ? 'px-2.5 py-1 text-xs' : 'px-3.5 py-2 text-sm'
      } ${className}`}
    >
      <RefreshCw
        className={`shrink-0 ${isSmall ? 'w-3.5 h-3.5' : 'w-4 h-4'} ${
          isGenerating ? 'animate-spin' : ''
        }`}
        aria-hidden="true"
      />
      <span>{isGenerating ? 'Retrying…' : 'Retry'}</span>
    </button>
  );
};
