import React, { useState } from 'react';
import { Download, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import { DownloadStatus } from '../types/audio.types';
import { audioService } from '../services/audioService';
import { resolveMimeExtension } from '../utils/audioUtils';

export interface AudioDownloadButtonProps {
  downloadUrl?: string;
  audioUrl?: string;
  generationId?: number | string;
  voiceName?: string;
  audioFormat?: string;
  contentType?: string;
  disabled?: boolean;
  className?: string;
}

export const AudioDownloadButton: React.FC<AudioDownloadButtonProps> = ({
  downloadUrl,
  audioUrl,
  generationId,
  voiceName,
  audioFormat,
  contentType,
  disabled = false,
  className = '',
}) => {
  const [status, setStatus] = useState<DownloadStatus>('idle');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const effectiveUrl = downloadUrl || audioUrl;

  const handleDownload = async () => {
    if (!effectiveUrl || status === 'downloading') return;

    setStatus('downloading');
    setErrorMessage(null);

    const ext = resolveMimeExtension(contentType, audioFormat);
    const voiceTag = voiceName ? voiceName.toLowerCase().replace(/\s+/g, '-') : 'speech';
    const genTag = generationId ? `-${generationId}` : '';
    const suggestedFilename = `bloop-${voiceTag}${genTag}.${ext}`;

    try {
      await audioService.downloadAudio(effectiveUrl, suggestedFilename, 'bloop-speech', ext);
      setStatus('downloaded');
      setTimeout(() => {
        setStatus('idle');
      }, 3000);
    } catch (err: unknown) {
      setStatus('error');
      setErrorMessage(
        err instanceof Error ? err.message : 'Download failed. Please try again.'
      );
      setTimeout(() => {
        setStatus('idle');
      }, 5000);
    }
  };

  if (!effectiveUrl) {
    return null;
  }

  return (
    <div className={`relative inline-flex items-center ${className}`}>
      <button
        type="button"
        onClick={handleDownload}
        disabled={disabled || status === 'downloading'}
        aria-label="Download generated audio file"
        title={
          status === 'error'
            ? errorMessage || 'Download failed'
            : status === 'downloaded'
            ? 'Downloaded to your device'
            : 'Download audio file'
        }
        className={`flex items-center space-x-2 px-3.5 py-2 rounded-xl text-xs font-semibold border transition shadow-sm focus:outline-none focus:ring-2 focus:ring-bloop-500/50 disabled:opacity-50 disabled:cursor-not-allowed ${
          status === 'error'
            ? 'bg-rose-950/40 border-rose-500/40 text-rose-300 hover:bg-rose-900/50'
            : status === 'downloaded'
            ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-300'
            : 'bg-slate-900/80 hover:bg-slate-800 border-white/10 text-slate-200 hover:text-white'
        }`}
      >
        {status === 'downloading' ? (
          <>
            <Loader2 className="w-3.5 h-3.5 animate-spin text-bloop-400" aria-hidden="true" />
            <span>Downloading…</span>
          </>
        ) : status === 'downloaded' ? (
          <>
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" aria-hidden="true" />
            <span>Saved!</span>
          </>
        ) : status === 'error' ? (
          <>
            <AlertCircle className="w-3.5 h-3.5 text-rose-400" aria-hidden="true" />
            <span>Retry Download</span>
          </>
        ) : (
          <>
            <Download className="w-3.5 h-3.5 text-slate-300 group-hover:text-white" aria-hidden="true" />
            <span>Download</span>
          </>
        )}
      </button>

      {/* Error Tooltip Banner */}
      {status === 'error' && errorMessage && (
        <span
          role="alert"
          className="absolute -top-8 left-1/2 -translate-x-1/2 whitespace-nowrap bg-rose-950 text-rose-200 text-[10px] px-2 py-0.5 rounded border border-rose-800 shadow-md pointer-events-none"
        >
          {errorMessage}
        </span>
      )}
    </div>
  );
};
