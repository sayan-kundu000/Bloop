import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Button } from '../ui';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // In development or controlled logging, log non-sensitive diagnostics
    if (process.env.NODE_ENV !== 'production') {
      console.error('[ErrorBoundary caught error]:', error, errorInfo);
    }
  }

  public handleReset = (): void => {
    this.setState({ hasError: false, error: null });
    window.location.href = '/workspace';
  };

  public handleRetry = (): void => {
    this.setState({ hasError: false, error: null });
  };

  public render(): ReactNode {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen bg-[#0b0f19] flex items-center justify-center p-4">
          <div className="max-w-md w-full glass-panel border border-rose-900/50 rounded-2xl p-6 text-center shadow-2xl">
            <div className="w-12 h-12 rounded-xl bg-rose-500/10 text-rose-400 mx-auto flex items-center justify-center mb-4 border border-rose-500/20">
              <svg
                className="w-6 h-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>

            <h2 className="text-xl font-bold text-slate-100 font-['Outfit'] mb-2">
              Something went wrong
            </h2>
            <p className="text-sm text-slate-400 mb-6">
              An unexpected application error occurred while rendering this screen.
              Your speech text and settings remain safe.
            </p>

            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Button
                variant="secondary"
                size="sm"
                onClick={this.handleRetry}
              >
                Try Again
              </Button>
              <Button
                variant="primary"
                size="sm"
                onClick={this.handleReset}
              >
                Return to Workspace
              </Button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
