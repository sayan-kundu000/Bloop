/**
 * Frontend API Error Normalization Layer
 * Provides normalized FrontendApiError class, status mapping, and friendly message resolution.
 */

export interface ErrorDetailMap {
  [key: string]: unknown;
}

export class FrontendApiError extends Error {
  public readonly code: string;
  public readonly status?: number;
  public readonly details?: unknown;
  public readonly timestamp: string;

  constructor(
    message: string,
    code: string = 'UNKNOWN_ERROR',
    status?: number,
    details?: unknown
  ) {
    super(message);
    this.name = 'FrontendApiError';
    this.code = code;
    this.status = status;
    this.details = details;
    this.timestamp = new Date().toISOString();

    // Maintain prototype chain for instanceof checks across bundles
    Object.setPrototypeOf(this, FrontendApiError.prototype);
  }

  /**
   * Helper predicates for UI routing and reaction
   */
  public isAuthError(): boolean {
    return this.status === 401 || this.code === 'UNAUTHORIZED' || this.code === 'INVALID_CREDENTIALS';
  }

  public isForbidden(): boolean {
    return this.status === 403 || this.code === 'FORBIDDEN';
  }

  public isNotFound(): boolean {
    return this.status === 404 || this.code === 'RESOURCE_NOT_FOUND';
  }

  public isConflict(): boolean {
    return this.status === 409 || this.code === 'ALREADY_EXISTS' || this.code === 'CONFLICT';
  }

  public isValidationError(): boolean {
    return this.status === 422 || this.code === 'VALIDATION_ERROR';
  }

  public isRateLimit(): boolean {
    return this.status === 429 || this.code === 'RATE_LIMIT_EXCEEDED';
  }

  public isServerError(): boolean {
    return typeof this.status === 'number' && this.status >= 500;
  }

  public isNetworkError(): boolean {
    return this.code === 'NETWORK_ERROR' || !this.status;
  }
}

/**
 * Standard friendly messages by HTTP status code
 */
const STATUS_MESSAGE_MAP: Record<number, string> = {
  400: 'The request could not be processed due to invalid parameters.',
  401: 'Your session has expired or you are not signed in. Please log in.',
  403: 'You do not have permission to perform this action.',
  404: 'The requested resource could not be found.',
  409: 'This operation conflicts with an existing resource.',
  422: 'Validation failed. Please check your inputs and try again.',
  429: 'You have reached the current request limit. Please try again later.',
  500: 'A backend server error occurred. Please try again shortly.',
  502: 'The server is currently unreachable. Please check your connection.',
  503: 'The speech generation service is temporarily unavailable. Please try again later.',
};

/**
 * Known error code translations for user-friendly UI display
 */
const CODE_MESSAGE_MAP: Record<string, string> = {
  TEXT_EMPTY: 'Please enter some text before generating speech.',
  TEXT_TOO_LONG: 'The entered text exceeds the maximum character limit.',
  INVALID_LANGUAGE: 'The selected language is invalid or unsupported.',
  INVALID_VOICE: 'The selected voice is unavailable. Please select another voice.',
  VOICE_NOT_FOUND: 'The selected voice is unavailable. Please select another voice.',
  VOICE_LANGUAGE_MISMATCH: 'The selected voice is not available for this language.',
  TTS_PROVIDER_UNAVAILABLE: 'The voice synthesis provider is temporarily unavailable. Please try again shortly.',
  TTS_PROVIDER_RATE_LIMITED: 'Provider rate limit reached. Please wait a moment before trying again.',
  TTS_GENERATION_FAILED: 'Speech generation could not be completed. Please try again.',
  AUDIO_GENERATION_FAILED: 'Speech audio generation failed. Please try again.',
  GENERATION_FAILED: 'Speech generation could not be completed. Please try again.',
  PROVIDER_ERROR: 'Voice provider encountered an issue. Please try again.',
  PROVIDER_TIMEOUT: 'Speech generation took too long. Please try again.',
  RATE_LIMIT_EXCEEDED: 'Too many requests. Please wait a moment before trying again.',
  AUTHENTICATION_REQUIRED: 'Session expired. Please sign in again.',
  AUTHENTICATION_FAILED: 'Authentication failed. Please sign in again.',
  ACCESS_DENIED: 'You do not have permission to perform this action.',
  FORBIDDEN: 'You do not have permission to perform this action.',
  SERVICE_UNAVAILABLE: 'The speech generation service is temporarily unavailable. Please try again later.',
  NETWORK_ERROR: 'Unable to connect to the Bloop server. Please check your internet connection.',
};

/**
 * Converts any caught error into a normalized FrontendApiError.
 */
export function normalizeApiError(error: unknown): FrontendApiError {
  if (error instanceof FrontendApiError) {
    return error;
  }

  if (typeof error === 'object' && error !== null) {
    const errObj = error as Record<string, any>;

    // Handle Axios error structure
    if (errObj.isAxiosError || errObj.response) {
      const response = errObj.response;
      const status = response?.status;
      const responseData = response?.data;

      // Extract backend error code and message
      const code =
        responseData?.error?.code ||
        responseData?.code ||
        (status ? `HTTP_${status}` : 'NETWORK_ERROR');

      let message =
        responseData?.error?.message ||
        responseData?.detail?.message ||
        responseData?.detail ||
        (code && CODE_MESSAGE_MAP[code]) ||
        (status && STATUS_MESSAGE_MAP[status]) ||
        errObj.message ||
        'An unexpected error occurred.';

      // Detail could be a string or object from FastAPI
      if (typeof message !== 'string') {
        message = JSON.stringify(message);
      }

      const details = responseData?.error?.details || responseData?.details;

      return new FrontendApiError(message, code, status, details);
    }

    // Standard JavaScript Error
    if (error instanceof Error) {
      const isNetwork = error.message.toLowerCase().includes('network') || error.message.toLowerCase().includes('failed to fetch');
      return new FrontendApiError(
        isNetwork ? CODE_MESSAGE_MAP.NETWORK_ERROR : error.message,
        isNetwork ? 'NETWORK_ERROR' : 'CLIENT_ERROR'
      );
    }
  }

  return new FrontendApiError(
    typeof error === 'string' ? error : 'An unexpected error occurred.',
    'UNKNOWN_ERROR'
  );
}
