import { AudioPlayerErrorCode } from '../types/audio.types';

/**
 * Formats a duration in seconds into a standardized Bloop timestamp string.
 * Examples:
 *   0      -> "00:00"
 *   5      -> "00:05"
 *   65     -> "01:05"
 *   125    -> "02:05"
 *   3665   -> "01:01:05"
 *
 * Edge cases (NaN, Infinity, negative) are clamped safely to "00:00".
 */
export function formatDuration(seconds: number | undefined | null): string {
  if (seconds === undefined || seconds === null || isNaN(seconds) || !isFinite(seconds) || seconds < 0) {
    return '00:00';
  }

  const totalSecs = Math.floor(seconds);
  const hours = Math.floor(totalSecs / 3600);
  const minutes = Math.floor((totalSecs % 3600) / 60);
  const secs = totalSecs % 60;

  const pad = (n: number): string => (n < 10 ? `0${n}` : `${n}`);

  if (hours > 0) {
    return `${pad(hours)}:${pad(minutes)}:${pad(secs)}`;
  }
  return `${pad(minutes)}:${pad(secs)}`;
}

/**
 * Clamps a playback seek time between 0 and duration.
 */
export function clampTime(time: number, duration: number): number {
  if (isNaN(time) || !isFinite(time) || time < 0) return 0;
  if (isNaN(duration) || !isFinite(duration) || duration <= 0) return 0;
  return Math.min(Math.max(0, time), duration);
}

/**
 * Resolves the appropriate file extension based on MIME type or format hint.
 */
export function resolveMimeExtension(contentType?: string, audioFormat?: string): string {
  const normType = (contentType || '').toLowerCase().trim();
  const normFormat = (audioFormat || '').toLowerCase().trim();

  if (normType.includes('wav') || normFormat === 'wav') return 'wav';
  if (normType.includes('ogg') || normFormat === 'ogg') return 'ogg';
  if (normType.includes('webm') || normFormat === 'webm') return 'webm';
  if (normType.includes('flac') || normFormat === 'flac') return 'flac';
  if (normType.includes('aac') || normFormat === 'aac') return 'aac';
  if (normType.includes('mpeg') || normType.includes('mp3') || normFormat === 'mp3') return 'mp3';

  return 'mp3';
}

/**
 * Sanitizes a candidate filename to prevent path traversal, illegal characters,
 * executable names, and excessive length.
 */
export function sanitizeFilename(
  rawName?: string,
  fallback = 'bloop-speech',
  extension = 'mp3'
): string {
  const cleanExt = extension.replace(/^\./, '').trim().toLowerCase() || 'mp3';

  if (!rawName || typeof rawName !== 'string' || rawName.trim() === '') {
    return `${fallback}.${cleanExt}`;
  }

  // Remove path traversal and illegal filesystem characters: / \ : * ? " < > | \0
  let clean = rawName
    .replace(/\.\./g, '')
    .replace(/[<>:"/\\|?*\x00-\x1F]/g, '')
    .replace(/\s+/g, '-')
    .trim();

  // Strip trailing extension if already present to avoid double extension (e.g. .mp3.mp3)
  const extRegex = new RegExp(`\\.${cleanExt}$`, 'i');
  clean = clean.replace(extRegex, '');

  // Truncate to maximum 60 characters
  if (clean.length > 60) {
    clean = clean.substring(0, 60).replace(/[-_]+$/, '');
  }

  if (!clean) {
    return `${fallback}.${cleanExt}`;
  }

  return `${clean}.${cleanExt}`;
}

/**
 * Normalizes technical audio errors into user-friendly messages without leaking
 * sensitive internals, credentials, or raw stack traces.
 */
export function getAudioErrorMessage(code: AudioPlayerErrorCode): string {
  switch (code) {
    case 'AUDIO_LOAD_FAILED':
      return 'Audio resource could not be loaded. Please check your connection and try again.';
    case 'AUDIO_PLAYBACK_FAILED':
      return 'Playback failed to start. Browser policies may require direct user interaction.';
    case 'AUDIO_UNSUPPORTED':
      return 'This browser does not support this audio format. You can still download the file directly.';
    case 'AUDIO_RESOURCE_EXPIRED':
      return 'The temporary audio resource has expired. Please regenerate speech to continue.';
    case 'AUDIO_NETWORK_ERROR':
      return 'Network connection interrupted during audio playback. Please retry.';
    default:
      return 'An unexpected audio error occurred. Please try again.';
  }
}
