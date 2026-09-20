import React from 'react';
import { Volume2, Sparkles, AlertCircle, Clock } from 'lucide-react';
import { AudioSource } from '../types/audio.types';
import { TTSResponse } from '../../../types';
import { useAudioPlayer } from '../hooks/useAudioPlayer';
import { AudioControls } from './AudioControls';
import { AudioProgress } from './AudioProgress';
import { VolumeControl } from './VolumeControl';
import { AudioDownloadButton } from './AudioDownloadButton';
import { AudioStatus } from './AudioStatus';

export interface AudioPlayerProps {
  source?: AudioSource | null;
  result?: TTSResponse | null;
  currentText?: string;
  autoPlay?: boolean;
  className?: string;
}

export const AudioPlayer: React.FC<AudioPlayerProps> = ({
  source,
  result,
  currentText,
  autoPlay = false,
  className = '',
}) => {
  // Normalize source from either AudioSource or TTSResponse
  const effectiveSource: AudioSource | null = source
    ? source
    : result
    ? {
        audioUrl: result.audio_url,
        downloadUrl: result.download_url,
        title: result.voice_name || 'Generated Speech',
        voiceName: result.voice_name,
        duration: result.duration_seconds,
        audioFormat: result.audio_format,
        contentType: result.content_type,
        generationId: result.generation_id,
        text: result.text,
      }
    : null;

  const player = useAudioPlayer(effectiveSource, { autoPlay });

  // Detect if workspace text has diverged from this audio's synthesized text
  const isTextDiverged =
    Boolean(currentText && effectiveSource?.text && currentText.trim() !== effectiveSource.text.trim());

  // Empty state when no audio source is present
  if (!effectiveSource || !effectiveSource.audioUrl) {
    return (
      <div
        role="region"
        aria-label="Speech Audio Player"
        className={`glass-panel rounded-2xl p-6 border border-white/5 text-center flex flex-col items-center justify-center space-y-3 ${className}`}
      >
        <div className="w-12 h-12 rounded-2xl bg-slate-900/60 border border-white/5 flex items-center justify-center text-slate-500">
          <Volume2 className="w-6 h-6" aria-hidden="true" />
        </div>
        <div>
          <p className="text-sm font-semibold text-slate-300">No generated speech yet</p>
          <p className="text-xs text-slate-500 mt-0.5">
            Type text in the workspace and click Generate Speech to listen and download.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div
      role="region"
      aria-label="Bloop Audio Player"
      className={`glass-panel rounded-2xl p-5 sm:p-6 border border-white/10 shadow-xl space-y-4 relative overflow-hidden transition-all duration-200 ${className}`}
    >
      {/* Decorative ambient gradient */}
      <div className="absolute top-0 right-0 w-36 h-36 bg-bloop-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header Info */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-white/5 pb-3">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-xl bg-bloop-600/20 border border-bloop-500/30 flex items-center justify-center text-bloop-400 shrink-0">
            <Volume2 className="w-4 h-4" aria-hidden="true" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-white leading-tight">
              {effectiveSource.title || 'Synthesized Speech'}
            </h4>
            <div className="flex items-center space-x-2 text-[11px] text-slate-400 mt-0.5">
              {effectiveSource.voiceName && (
                <span>Voice: <strong className="text-slate-200">{effectiveSource.voiceName}</strong></span>
              )}
              {effectiveSource.duration && (
                <>
                  <span className="text-slate-600">•</span>
                  <span className="flex items-center space-x-1">
                    <Clock className="w-3 h-3 text-slate-500" aria-hidden="true" />
                    <span>~{effectiveSource.duration}s</span>
                  </span>
                </>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {effectiveSource.audioFormat && (
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-900 border border-white/10 text-slate-300 uppercase">
              {effectiveSource.audioFormat}
            </span>
          )}
          <AudioDownloadButton
            downloadUrl={effectiveSource.downloadUrl}
            audioUrl={effectiveSource.audioUrl}
            generationId={effectiveSource.generationId}
            voiceName={effectiveSource.voiceName}
            audioFormat={effectiveSource.audioFormat}
            contentType={effectiveSource.contentType}
          />
        </div>
      </div>

      {/* Text Divergence Advisory */}
      {isTextDiverged && (
        <div
          role="status"
          className="flex items-center space-x-2 p-2.5 rounded-xl bg-amber-950/30 border border-amber-500/20 text-amber-300 text-xs"
        >
          <AlertCircle className="w-4 h-4 shrink-0 text-amber-400" aria-hidden="true" />
          <span>
            The workspace text has changed since this audio was synthesized. The player continues to play the previously generated speech.
          </span>
        </div>
      )}

      {/* Progress Track & Scrubber */}
      <AudioProgress
        currentTime={player.currentTime}
        duration={player.duration}
        bufferedProgress={player.bufferedProgress}
        onSeek={player.seek}
        disabled={player.isLoading || Boolean(player.error)}
      />

      {/* Controls & Volume Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 pt-1">
        {/* Playback Buttons */}
        <AudioControls
          status={player.status}
          isPlaying={player.isPlaying}
          isEnded={player.isEnded}
          isLoading={player.isLoading}
          onTogglePlay={player.togglePlay}
          onRestart={player.restart}
          onSeekRelative={(delta) => player.seek(player.currentTime + delta)}
        />

        {/* Status / Error feedback */}
        <AudioStatus
          status={player.status}
          isLoading={player.isLoading}
          isBuffering={player.isBuffering}
          error={player.error}
          onRetry={player.retry}
        />

        {/* Volume Controls */}
        <VolumeControl
          volume={player.volume}
          isMuted={player.isMuted}
          onVolumeChange={player.setVolume}
          onToggleMute={player.toggleMute}
          disabled={Boolean(player.error)}
        />
      </div>
    </div>
  );
};
