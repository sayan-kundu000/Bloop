import React, { useRef, useEffect } from 'react';
import { Play, Pause, Volume2, VolumeX, Download, X, Gauge } from 'lucide-react';
import { useAudioStore } from '../../stores/audioStore';

export const AudioPlayerBar: React.FC = () => {
  const {
    currentAudioUrl,
    currentTitle,
    isPlaying,
    currentTime,
    duration,
    volume,
    speed,
    togglePlay,
    setCurrentTime,
    setDuration,
    setVolume,
    setSpeed,
    stopAudio,
  } = useAudioStore();

  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.play().catch(() => {});
      } else {
        audioRef.current.pause();
      }
    }
  }, [isPlaying, currentAudioUrl]);

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = volume;
    }
  }, [volume]);

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.playbackRate = speed;
    }
  }, [speed]);

  if (!currentAudioUrl) return null;

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration || 0);
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = parseFloat(e.target.value);
    if (audioRef.current) {
      audioRef.current.currentTime = time;
    }
    setCurrentTime(time);
  };

  const handleSpeedCycle = () => {
    const speeds = [0.75, 1.0, 1.25, 1.5, 2.0];
    const nextIdx = (speeds.indexOf(speed) + 1) % speeds.length;
    setSpeed(speeds[nextIdx]);
  };

  const formatTime = (secs: number) => {
    if (isNaN(secs) || secs < 0) return '0:00';
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  const downloadUrl = currentAudioUrl.includes('/audio/')
    ? currentAudioUrl.replace('/audio/', '/download/')
    : currentAudioUrl;

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 bg-slate-900/95 backdrop-blur-xl border-t border-bloop-500/20 shadow-2xl shadow-black/80 px-4 py-3">
      <audio
        ref={audioRef}
        src={currentAudioUrl}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onEnded={() => useAudioStore.getState().pauseAudio()}
      />

      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
        {/* Track Title */}
        <div className="flex items-center space-x-3 w-full sm:w-1/4">
          <div className="w-10 h-10 rounded-lg bg-bloop-600/30 border border-bloop-500/40 flex items-center justify-center shrink-0">
            <Volume2 className="w-5 h-5 text-bloop-400 animate-pulse" />
          </div>
          <div className="truncate">
            <p className="text-sm font-semibold text-white truncate">{currentTitle}</p>
            <p className="text-xs text-slate-400">Bloop Speech Player</p>
          </div>
        </div>

        {/* Player Controls & Scrubber */}
        <div className="flex flex-col items-center w-full sm:w-2/4 gap-1.5">
          <div className="flex items-center space-x-4">
            <button
              onClick={togglePlay}
              className="w-10 h-10 rounded-full bg-bloop-600 hover:bg-bloop-500 text-white flex items-center justify-center shadow-lg shadow-bloop-600/30 transition transform hover:scale-105"
            >
              {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5 translate-x-0.5" />}
            </button>
          </div>

          <div className="flex items-center space-x-3 w-full">
            <span className="text-xs font-mono text-slate-400 w-10 text-right">{formatTime(currentTime)}</span>
            <input
              type="range"
              min={0}
              max={duration || 100}
              step={0.1}
              value={currentTime}
              onChange={handleSeek}
              className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-bloop-500"
            />
            <span className="text-xs font-mono text-slate-400 w-10">{formatTime(duration)}</span>
          </div>
        </div>

        {/* Actions: Speed, Volume, Download, Close */}
        <div className="flex items-center justify-end space-x-2.5 w-full sm:w-1/4">
          <button
            onClick={handleSpeedCycle}
            title="Playback Speed"
            className="flex items-center space-x-1 px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-xs font-mono text-slate-300 border border-white/5 transition"
          >
            <Gauge className="w-3.5 h-3.5 text-bloop-400" />
            <span>{speed}x</span>
          </button>

          <div className="flex items-center space-x-1.5">
            <button
              onClick={() => setVolume(volume > 0 ? 0 : 1)}
              className="p-1.5 text-slate-400 hover:text-white transition"
            >
              {volume === 0 ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
            </button>
            <input
              type="range"
              min={0}
              max={1}
              step={0.05}
              value={volume}
              onChange={(e) => setVolume(parseFloat(e.target.value))}
              className="w-16 h-1 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-bloop-500"
            />
          </div>

          <a
            href={downloadUrl}
            download
            title="Download Audio"
            className="p-2 rounded-lg bg-bloop-600/20 hover:bg-bloop-600/30 text-bloop-400 border border-bloop-500/30 transition"
          >
            <Download className="w-4 h-4" />
          </a>

          <button
            onClick={stopAudio}
            title="Close Player"
            className="p-2 text-slate-500 hover:text-slate-300 transition"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
