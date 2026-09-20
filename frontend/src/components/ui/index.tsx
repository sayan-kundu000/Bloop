import React, { useEffect, useRef } from 'react';

// ---------------------------------------------------------------------------
// 1. Button Primitive
// ---------------------------------------------------------------------------
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  className = '',
  disabled,
  ...props
}) => {
  const baseStyles =
    'inline-flex items-center justify-center font-medium rounded-lg transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900 disabled:opacity-50 disabled:cursor-not-allowed';

  const sizeStyles = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base',
  };

  const variantStyles = {
    primary:
      'bg-indigo-600 hover:bg-indigo-500 text-white focus:ring-indigo-500 shadow-md shadow-indigo-600/20 active:scale-[0.99]',
    secondary:
      'bg-slate-800 hover:bg-slate-700 text-slate-100 focus:ring-slate-600 border border-slate-700 active:scale-[0.99]',
    outline:
      'border border-slate-700 text-slate-300 hover:bg-slate-800/60 focus:ring-slate-500 active:scale-[0.99]',
    danger:
      'bg-rose-600 hover:bg-rose-500 text-white focus:ring-rose-500 shadow-md shadow-rose-600/20 active:scale-[0.99]',
    ghost:
      'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40 focus:ring-slate-500',
  };

  return (
    <button
      className={`${baseStyles} ${sizeStyles[size]} ${variantStyles[variant]} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <span
          className="w-4 h-4 mr-2 border-2 border-current border-t-transparent rounded-full animate-spin"
          aria-hidden="true"
        />
      ) : null}
      {children}
    </button>
  );
};

// ---------------------------------------------------------------------------
// 2. Input Primitive
// ---------------------------------------------------------------------------
export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  hasError?: boolean;
}

export const Input: React.FC<InputProps> = ({
  hasError = false,
  className = '',
  ...props
}) => {
  return (
    <input
      className={`w-full px-3 py-2 text-sm bg-slate-900/80 border ${
        hasError
          ? 'border-rose-500 focus:border-rose-500 focus:ring-rose-500/50'
          : 'border-slate-700 focus:border-indigo-500 focus:ring-indigo-500/50'
      } rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
      {...props}
    />
  );
};

// ---------------------------------------------------------------------------
// 3. Textarea Primitive
// ---------------------------------------------------------------------------
export interface TextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  hasError?: boolean;
  maxCharacters?: number;
  currentCharCount?: number;
  resize?: 'none' | 'vertical' | 'horizontal' | 'both';
}

export const Textarea: React.FC<TextareaProps> = ({
  hasError = false,
  maxCharacters,
  currentCharCount,
  resize = 'vertical',
  className = '',
  value,
  ...props
}) => {
  const resizeClass = {
    none: 'resize-none',
    vertical: 'resize-y',
    horizontal: 'resize-x',
    both: 'resize',
  }[resize];

  // Derive current length if not explicitly passed
  const charLength =
    currentCharCount !== undefined
      ? currentCharCount
      : typeof value === 'string'
      ? value.length
      : 0;

  const isOverLimit = maxCharacters ? charLength > maxCharacters : false;

  return (
    <div className="w-full">
      <textarea
        value={value}
        className={`w-full px-3.5 py-2.5 text-sm bg-slate-900/80 border ${
          hasError || isOverLimit
            ? 'border-rose-500 focus:border-rose-500 focus:ring-rose-500/50'
            : 'border-slate-700 focus:border-indigo-500 focus:ring-indigo-500/50'
        } rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${resizeClass} ${className}`}
        {...props}
      />
      {maxCharacters !== undefined && (
        <div className="mt-1 flex justify-end">
          <span
            className={`text-xs font-mono ${
              isOverLimit ? 'text-rose-400 font-semibold' : 'text-slate-500'
            }`}
          >
            {charLength} / {maxCharacters} chars
          </span>
        </div>
      )}
    </div>
  );
};

// ---------------------------------------------------------------------------
// 4. Select Primitive
// ---------------------------------------------------------------------------
export interface SelectOption {
  value: string | number;
  label: string;
  disabled?: boolean;
}

export interface SelectProps
  extends React.SelectHTMLAttributes<HTMLSelectElement> {
  options?: SelectOption[];
  hasError?: boolean;
}

export const Select: React.FC<SelectProps> = ({
  options,
  children,
  hasError = false,
  className = '',
  ...props
}) => {
  return (
    <div className="relative w-full">
      <select
        className={`w-full appearance-none px-3.5 py-2 pr-9 text-sm bg-slate-900/80 border ${
          hasError
            ? 'border-rose-500 focus:border-rose-500 focus:ring-rose-500/50'
            : 'border-slate-700 focus:border-indigo-500 focus:ring-indigo-500/50'
        } rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
        {...props}
      >
        {options
          ? options.map((opt) => (
              <option
                key={opt.value}
                value={opt.value}
                disabled={opt.disabled}
                className="bg-slate-900 text-slate-100"
              >
                {opt.label}
              </option>
            ))
          : children}
      </select>
      <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2.5 text-slate-400">
        <svg
          className="w-4 h-4 fill-current"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20"
        >
          <path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" />
        </svg>
      </div>
    </div>
  );
};

// ---------------------------------------------------------------------------
// 5. Card Primitive
// ---------------------------------------------------------------------------
export const Card: React.FC<{ children: React.ReactNode; className?: string }> = ({
  children,
  className = '',
}) => {
  return (
    <div
      className={`bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 shadow-lg backdrop-blur-sm ${className}`}
    >
      {children}
    </div>
  );
};

// ---------------------------------------------------------------------------
// 6. Badge Primitive
// ---------------------------------------------------------------------------
export interface BadgeProps {
  children: React.ReactNode;
  variant?: 'indigo' | 'emerald' | 'amber' | 'rose' | 'slate' | 'quantum';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'indigo',
  className = '',
}) => {
  const variantStyles = {
    indigo: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
    emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    amber: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    rose: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
    slate: 'bg-slate-800 text-slate-400 border-slate-700',
    quantum: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
  };

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${variantStyles[variant]} ${className}`}
    >
      {children}
    </span>
  );
};

// ---------------------------------------------------------------------------
// 7. Modal / Dialog Primitive
// ---------------------------------------------------------------------------
export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: React.ReactNode;
  description?: React.ReactNode;
  children: React.ReactNode;
  footer?: React.ReactNode;
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl';
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  description,
  children,
  footer,
  maxWidth = 'md',
}) => {
  const modalRef = useRef<HTMLDivElement>(null);

  // Keyboard Escape listener
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const maxWidthClass = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    '2xl': 'max-w-2xl',
  }[maxWidth];

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm animate-in fade-in duration-150"
      role="dialog"
      aria-modal="true"
      aria-labelledby={title ? 'modal-title' : undefined}
      aria-describedby={description ? 'modal-description' : undefined}
    >
      {/* Backdrop click handler */}
      <div className="fixed inset-0" onClick={onClose} aria-hidden="true" />

      {/* Modal Dialog Content */}
      <div
        ref={modalRef}
        className={`relative w-full ${maxWidthClass} bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden z-10`}
      >
        {/* Header */}
        <div className="flex items-start justify-between px-6 pt-5 pb-4 border-b border-slate-800">
          <div>
            {title && (
              <h3
                id="modal-title"
                className="text-lg font-semibold text-slate-100 font-['Outfit']"
              >
                {title}
              </h3>
            )}
            {description && (
              <p
                id="modal-description"
                className="text-xs text-slate-400 mt-1"
              >
                {description}
              </p>
            )}
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-200 p-1 rounded-lg hover:bg-slate-800 transition"
            aria-label="Close dialog"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Body */}
        <div className="px-6 py-4 max-h-[75vh] overflow-y-auto text-slate-200 text-sm">
          {children}
        </div>

        {/* Optional Footer */}
        {footer && (
          <div className="px-6 py-3.5 bg-slate-900/50 border-t border-slate-800 flex justify-end space-x-3">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
};

// ---------------------------------------------------------------------------
// 8. ConfirmDialog Primitive
// ---------------------------------------------------------------------------
export interface ConfirmDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  isDestructive?: boolean;
  isLoading?: boolean;
}

export const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  isDestructive = false,
  isLoading = false,
}) => {
  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      maxWidth="sm"
      footer={
        <>
          <Button
            variant="secondary"
            size="sm"
            onClick={onClose}
            disabled={isLoading}
          >
            {cancelLabel}
          </Button>
          <Button
            variant={isDestructive ? 'danger' : 'primary'}
            size="sm"
            onClick={onConfirm}
            isLoading={isLoading}
          >
            {confirmLabel}
          </Button>
        </>
      }
    >
      <p className="text-sm text-slate-300">{message}</p>
    </Modal>
  );
};

// ---------------------------------------------------------------------------
// 9. Spinner Primitive
// ---------------------------------------------------------------------------
export interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  label?: string;
}

export const Spinner: React.FC<SpinnerProps> = ({
  size = 'md',
  className = '',
  label = 'Loading...',
}) => {
  const sizeClass = {
    sm: 'w-4 h-4 border-2',
    md: 'w-8 h-8 border-3',
    lg: 'w-12 h-12 border-4',
  }[size];

  return (
    <div
      role="status"
      className={`inline-flex items-center justify-center ${className}`}
    >
      <div
        className={`${sizeClass} border-indigo-500 border-t-transparent rounded-full animate-spin`}
        aria-hidden="true"
      />
      <span className="sr-only">{label}</span>
    </div>
  );
};

// ---------------------------------------------------------------------------
// 10. Skeleton Primitive
// ---------------------------------------------------------------------------
export interface SkeletonProps {
  className?: string;
  rounded?: 'sm' | 'md' | 'lg' | 'full';
}

export const Skeleton: React.FC<SkeletonProps> = ({
  className = 'w-full h-4',
  rounded = 'md',
}) => {
  const roundedClass = {
    sm: 'rounded-sm',
    md: 'rounded-md',
    lg: 'rounded-lg',
    full: 'rounded-full',
  }[rounded];

  return (
    <div
      className={`bg-slate-800/70 animate-pulse ${roundedClass} ${className}`}
      aria-hidden="true"
    />
  );
};

// ---------------------------------------------------------------------------
// 11. EmptyState Primitive
// ---------------------------------------------------------------------------
export interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  icon,
  action,
  className = '',
}) => {
  return (
    <div
      className={`flex flex-col items-center justify-center p-8 text-center bg-slate-900/40 rounded-xl border border-slate-800/80 ${className}`}
    >
      {icon && <div className="mb-4 text-slate-400 text-3xl">{icon}</div>}
      <h3 className="text-base font-semibold text-slate-200">{title}</h3>
      {description && (
        <p className="mt-1 text-sm text-slate-400 max-w-sm">{description}</p>
      )}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
};

// ---------------------------------------------------------------------------
// 12. Tooltip Primitive
// ---------------------------------------------------------------------------
export interface TooltipProps {
  content: string;
  children: React.ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right';
}

export const Tooltip: React.FC<TooltipProps> = ({
  content,
  children,
  position = 'top',
}) => {
  const positionClasses = {
    top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 -translate-y-1/2 ml-2',
  }[position];

  return (
    <div className="relative group inline-block">
      {children}
      <div
        role="tooltip"
        className={`pointer-events-none absolute ${positionClasses} z-50 hidden group-hover:block group-focus-within:block px-2.5 py-1 text-xs font-medium text-slate-100 bg-slate-800 border border-slate-700 rounded shadow-md whitespace-nowrap`}
      >
        {content}
      </div>
    </div>
  );
};
