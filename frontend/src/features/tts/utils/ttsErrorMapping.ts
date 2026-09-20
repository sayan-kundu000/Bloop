import { FrontendApiError, normalizeApiError } from '../../../lib/api/errors';

/**
 * Standardized mapping of backend TTS domain error codes to human-readable user messages.
 * Prevents technical stack traces and internal provider details from leaking into the UI.
 */
export const TTS_ERROR_MESSAGE_MAP: Record<string, string> = {
  TEXT_EMPTY: 'Please enter some text before generating speech.',
  TEXT_TOO_LONG: 'The entered text exceeds the maximum allowable limit of 2,500 characters.',
  INVALID_LANGUAGE: 'The selected language is invalid or unsupported.',
  INVALID_VOICE: 'The selected voice could not be found. Please select another voice.',
  VOICE_LANGUAGE_MISMATCH: 'The selected voice is not available for this language.',
  TTS_PROVIDER_UNAVAILABLE: 'The voice synthesis provider is temporarily unavailable. Please try again shortly.',
  TTS_PROVIDER_RATE_LIMITED: 'Provider rate limit reached. Please wait a moment before trying again.',
  PROVIDER_ERROR: 'Voice provider encountered an issue. Please try again.',
  PROVIDER_TIMEOUT: 'Speech generation took too long. Please try again.',
  RATE_LIMIT_EXCEEDED: 'Too many requests. Please wait a moment before trying again.',
  AUTHENTICATION_REQUIRED: 'Session expired. Please sign in again.',
  AUTHENTICATION_FAILED: 'Authentication failed. Please sign in again.',
  ACCESS_DENIED: 'You do not have permission to synthesize speech.',
  FORBIDDEN: 'You do not have permission to synthesize speech.',
  TTS_GENERATION_FAILED: 'Speech generation could not be completed. Please try again.',
  AUDIO_GENERATION_FAILED: 'Speech audio generation failed. Please try again.',
  SERVICE_UNAVAILABLE: 'Speech generation service is temporarily unavailable.',
  NETWORK_ERROR: "We couldn't reach Bloop. Check your connection and try again.",
  RESOURCE_NOT_FOUND: 'The requested resource was not found.',
};

/**
 * Converts any caught error into a friendly, safe user-facing message.
 */
export function getFriendlyTTSErrorMessage(error: unknown): string {
  if (!error) return 'An unexpected error occurred.';

  const normalized = error instanceof FrontendApiError ? error : normalizeApiError(error);

  // 1. Direct code translation
  if (normalized.code && TTS_ERROR_MESSAGE_MAP[normalized.code]) {
    return TTS_ERROR_MESSAGE_MAP[normalized.code];
  }

  // 2. Status-based translations
  if (normalized.status === 401) {
    return TTS_ERROR_MESSAGE_MAP.AUTHENTICATION_REQUIRED;
  }
  if (normalized.status === 403) {
    return TTS_ERROR_MESSAGE_MAP.FORBIDDEN;
  }
  if (normalized.status === 429) {
    return TTS_ERROR_MESSAGE_MAP.RATE_LIMIT_EXCEEDED;
  }
  if (normalized.status === 503) {
    return TTS_ERROR_MESSAGE_MAP.SERVICE_UNAVAILABLE;
  }
  if (normalized.status && normalized.status >= 500) {
    return 'A server error occurred during synthesis. Please try again shortly.';
  }
  if (normalized.isNetworkError()) {
    return TTS_ERROR_MESSAGE_MAP.NETWORK_ERROR;
  }

  // 3. Fall back to normalized message if it doesn't leak secrets or stack traces
  const rawMessage = normalized.message || '';
  if (
    rawMessage &&
    !rawMessage.toLowerCase().includes('elevenlabs') &&
    !rawMessage.toLowerCase().includes('api_key') &&
    !rawMessage.toLowerCase().includes('stack')
  ) {
    return rawMessage;
  }

  return 'Speech generation could not be completed. Please try again.';
}

/**
 * Determines whether an error is transient and safe for user-triggered retry.
 * Excludes non-retryable issues like invalid text length, empty text, or 403 forbidden.
 */
export function isRetryableTTSError(error: unknown): boolean {
  if (!error) return false;

  const normalized = error instanceof FrontendApiError ? error : normalizeApiError(error);

  // Non-retryable validation and auth issues
  if (
    normalized.code === 'TEXT_EMPTY' ||
    normalized.code === 'TEXT_TOO_LONG' ||
    normalized.code === 'INVALID_LANGUAGE' ||
    normalized.code === 'INVALID_VOICE' ||
    normalized.code === 'VOICE_LANGUAGE_MISMATCH' ||
    normalized.status === 401 ||
    normalized.status === 403 ||
    normalized.code === 'AUTHENTICATION_REQUIRED' ||
    normalized.code === 'FORBIDDEN' ||
    normalized.code === 'ACCESS_DENIED'
  ) {
    return false;
  }

  // Rate limits should not be immediately retried
  if (normalized.status === 429 || normalized.code === 'RATE_LIMIT_EXCEEDED') {
    return false;
  }

  // Network errors, timeouts, provider glitches, and 5xx server errors are retryable
  if (
    normalized.isNetworkError() ||
    normalized.isServerError() ||
    normalized.code === 'PROVIDER_TIMEOUT' ||
    normalized.code === 'PROVIDER_ERROR' ||
    normalized.code === 'TTS_PROVIDER_UNAVAILABLE' ||
    normalized.code === 'SERVICE_UNAVAILABLE' ||
    normalized.code === 'TTS_GENERATION_FAILED' ||
    normalized.code === 'AUDIO_GENERATION_FAILED'
  ) {
    return true;
  }

  return false;
}
