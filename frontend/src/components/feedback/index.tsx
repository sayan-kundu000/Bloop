import React from 'react';

export interface AlertBannerProps {
  type?: 'info' | 'success' | 'warning' | 'error';
  title?: string;
  message: string;
  onClose?: () => void;
}

export const AlertBanner: React.FC<AlertBannerProps> = ({
  type = 'info',
  title,
  message,
  onClose,
}) => {
  const styles = {
    info: 'bg-blue-950/30 border-blue-800 text-blue-300',
    success: 'bg-emerald-950/30 border-emerald-800 text-emerald-300',
    warning: 'bg-amber-950/30 border-amber-800 text-amber-300',
    error: 'bg-rose-950/30 border-rose-800 text-rose-300',
  };

  return (
    <div className={`flex items-start justify-between p-4 rounded-lg border text-sm ${styles[type]}`}>
      <div className="flex-1">
        {title && <h5 className="font-semibold mb-0.5">{title}</h5>}
        <p>{message}</p>
      </div>
      {onClose && (
        <button
          onClick={onClose}
          className="ml-3 text-slate-400 hover:text-slate-200 transition-colors"
          aria-label="Close"
        >
          &times;
        </button>
      )}
    </div>
  );
};
