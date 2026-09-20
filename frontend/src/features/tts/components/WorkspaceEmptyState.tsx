import React from 'react';
import { Type } from 'lucide-react';

export interface WorkspaceEmptyStateProps {
  onLoadDefaultSample?: () => void;
}

export const WorkspaceEmptyState: React.FC<WorkspaceEmptyStateProps> = ({ onLoadDefaultSample }) => {
  return (
    <div className="flex items-center justify-between p-3.5 rounded-xl bg-slate-900/40 border border-slate-800/80 text-xs text-slate-400">
      <div className="flex items-center space-x-2.5">
        <Type className="w-4 h-4 text-bloop-400 shrink-0" aria-hidden="true" />
        <span>Enter or paste text to get started. You can also load a sample preset above.</span>
      </div>
      {onLoadDefaultSample && (
        <button
          type="button"
          onClick={onLoadDefaultSample}
          className="text-bloop-400 hover:text-bloop-300 font-medium whitespace-nowrap ml-2 hover:underline"
        >
          Insert Sample
        </button>
      )}
    </div>
  );
};
