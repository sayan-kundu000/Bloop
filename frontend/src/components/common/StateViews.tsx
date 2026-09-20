import React from 'react';

interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  icon,
  action,
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center bg-slate-900/40 rounded-xl border border-slate-800">
      {icon && <div className="mb-4 text-slate-400 text-4xl">{icon}</div>}
      <h3 className="text-lg font-semibold text-slate-200">{title}</h3>
      {description && <p className="mt-1 text-sm text-slate-400 max-w-sm">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
};

export const LoadingState: React.FC<{ message?: string }> = ({ message = 'Loading...' }) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center">
      <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
      <p className="mt-3 text-sm text-slate-400 font-medium">{message}</p>
    </div>
  );
};

export const ErrorState: React.FC<{ title?: string; message: string; onRetry?: () => void }> = ({
  title = 'An error occurred',
  message,
  onRetry,
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-6 text-center bg-red-950/20 border border-red-800/40 rounded-xl">
      <h4 className="text-base font-semibold text-red-400">{title}</h4>
      <p className="mt-1 text-sm text-slate-300">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-4 px-4 py-1.5 text-xs font-medium text-white bg-red-600 hover:bg-red-500 rounded-lg transition-colors"
        >
          Try Again
        </button>
      )}
    </div>
  );
};
