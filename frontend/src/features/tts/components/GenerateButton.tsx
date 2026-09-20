import React from 'react';
import { Volume2, Loader2 } from 'lucide-react';
import { Button } from '../../../components/ui';

export interface GenerateButtonProps {
  onClick: () => void;
  isGenerating?: boolean;
  disabled?: boolean;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const GenerateButton: React.FC<GenerateButtonProps> = ({
  onClick,
  isGenerating = false,
  disabled = false,
  className = '',
  size = 'lg',
}) => {
  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    if (disabled || isGenerating) {
      return;
    }
    onClick();
  };

  return (
    <Button
      type="button"
      variant="primary"
      size={size}
      onClick={handleClick}
      disabled={disabled || isGenerating}
      aria-busy={isGenerating}
      aria-label={isGenerating ? 'Generating speech, please wait' : 'Generate Speech'}
      className={`min-h-[44px] px-6 py-2.5 font-semibold text-sm shadow-lg shadow-bloop-600/30 transition-all flex items-center justify-center space-x-2 ${
        isGenerating ? 'cursor-wait opacity-90' : ''
      } ${className}`}
    >
      {isGenerating ? (
        <>
          <Loader2 className="w-4 h-4 animate-spin shrink-0 text-white" aria-hidden="true" />
          <span>Generating…</span>
        </>
      ) : (
        <>
          <Volume2 className="w-4 h-4 shrink-0" aria-hidden="true" />
          <span>Generate Speech</span>
        </>
      )}
    </Button>
  );
};
