import { describe, it, expect } from 'vitest';
import { FrontendApiError, normalizeApiError } from '../../lib/api/errors';

describe('API Error Normalization Layer', () => {
  describe('FrontendApiError', () => {
    it('initializes with correct properties and defaults', () => {
      const error = new FrontendApiError(
        'Speech generation failed',
        'GENERATION_FAILED',
        500,
        { reason: 'provider_timeout' }
      );

      expect(error.name).toBe('FrontendApiError');
      expect(error.message).toBe('Speech generation failed');
      expect(error.code).toBe('GENERATION_FAILED');
      expect(error.status).toBe(500);
      expect(error.details).toEqual({ reason: 'provider_timeout' });
      expect(typeof error.timestamp).toBe('string');
    });

    it('correctly reports predicate helpers', () => {
      const authErr = new FrontendApiError('Unauthorized', 'UNAUTHORIZED', 401);
      expect(authErr.isAuthError()).toBe(true);
      expect(authErr.isForbidden()).toBe(false);

      const rateLimitErr = new FrontendApiError('Rate limited', 'RATE_LIMIT_EXCEEDED', 429);
      expect(rateLimitErr.isRateLimit()).toBe(true);

      const notFoundErr = new FrontendApiError('Not found', 'NOT_FOUND', 404);
      expect(notFoundErr.isNotFound()).toBe(true);

      const conflictErr = new FrontendApiError('Conflict', 'ALREADY_EXISTS', 409);
      expect(conflictErr.isConflict()).toBe(true);

      const validationErr = new FrontendApiError('Validation failed', 'VALIDATION_ERROR', 422);
      expect(validationErr.isValidationError()).toBe(true);

      const serverErr = new FrontendApiError('Server error', 'INTERNAL_ERROR', 503);
      expect(serverErr.isServerError()).toBe(true);

      const netErr = new FrontendApiError('Failed to fetch', 'NETWORK_ERROR');
      expect(netErr.isNetworkError()).toBe(true);
    });
  });

  describe('normalizeApiError', () => {
    it('returns the same instance if already a FrontendApiError', () => {
      const original = new FrontendApiError('Existing', 'EXISTING_CODE', 400);
      const normalized = normalizeApiError(original);
      expect(normalized).toBe(original);
    });

    it('normalizes Axios-style response error structure', () => {
      const axiosLikeError = {
        isAxiosError: true,
        response: {
          status: 422,
          data: {
            success: false,
            error: {
              code: 'TEXT_EMPTY',
              message: 'Please enter some text before generating speech.',
              details: { field: 'text' },
            },
          },
        },
      };

      const normalized = normalizeApiError(axiosLikeError);
      expect(normalized).toBeInstanceOf(FrontendApiError);
      expect(normalized.code).toBe('TEXT_EMPTY');
      expect(normalized.status).toBe(422);
      expect(normalized.message).toBe('Please enter some text before generating speech.');
      expect(normalized.details).toEqual({ field: 'text' });
    });

    it('translates HTTP 429 rate limit responses into user-friendly message', () => {
      const rateLimitAxiosError = {
        response: {
          status: 429,
          data: {},
        },
      };

      const normalized = normalizeApiError(rateLimitAxiosError);
      expect(normalized.status).toBe(429);
      expect(normalized.message).toContain('request limit');
    });

    it('normalizes network connectivity errors', () => {
      const netError = new Error('Network Error: Failed to fetch');
      const normalized = normalizeApiError(netError);

      expect(normalized.code).toBe('NETWORK_ERROR');
      expect(normalized.isNetworkError()).toBe(true);
      expect(normalized.message).toContain('internet connection');
    });

    it('normalizes primitive string errors', () => {
      const normalized = normalizeApiError('Something strange happened');
      expect(normalized.message).toBe('Something strange happened');
      expect(normalized.code).toBe('UNKNOWN_ERROR');
    });
  });
});
