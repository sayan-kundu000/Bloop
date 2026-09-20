/**
 * Application Runtime Configuration
 * Centralizes environment variables, API endpoints, and system constraints.
 * 
 * SECURITY RULE:
 * This file and the entire frontend bundle must ONLY consume public configuration.
 * Never import or define secrets (API keys, JWT secrets, database credentials) here.
 */

export type EnvironmentProfile = 'development' | 'test' | 'production';

export interface AppConfig {
  readonly apiBaseUrl: string;
  readonly apiV1Url: string;
  readonly environment: EnvironmentProfile;
  readonly isProduction: boolean;
  readonly isDevelopment: boolean;
  readonly isTest: boolean;
  readonly queryClient: {
    readonly staleTimeMs: number;
    readonly retryCount: number;
    readonly timeoutMs: number;
  };
  readonly limits: {
    readonly minTextLength: number;
    readonly maxTextLength: number;
    readonly defaultSpeechRate: number;
    readonly defaultPitch: number;
  };
}

/**
 * Normalizes an API URL by stripping trailing slashes.
 */
export function normalizeApiUrl(url?: string): string {
  if (!url || typeof url !== 'string' || !url.trim()) {
    return 'http://localhost:8000';
  }
  return url.trim().replace(/\/+$/, '');
}

/**
 * Security audit helper: verifies that no private secrets or credentials
 * were inadvertently leaked into the client-side environment.
 */
function auditClientEnvironment(env: Record<string, any>): void {
  const forbiddenPatterns = [
    'DATABASE_URL',
    'JWT_SECRET',
    'SECRET_KEY',
    'ELEVENLABS',
    'PASSWORD',
    'PRIVATE_KEY',
  ];

  for (const key of Object.keys(env)) {
    for (const pattern of forbiddenPatterns) {
      if (key.toUpperCase().includes(pattern) && !key.startsWith('VITE_SAFE_')) {
        console.error(
          `[SECURITY AUDIT FAILURE] Prohibited secret variable '${key}' detected in frontend client environment!`
        );
      }
    }
  }
}

// Run security audit on client environment
if (typeof import.meta !== 'undefined' && import.meta.env) {
  auditClientEnvironment(import.meta.env);
}

const rawMode = (typeof import.meta !== 'undefined' && import.meta.env?.MODE) || 'development';
const environment: EnvironmentProfile =
  rawMode === 'production' ? 'production' : rawMode === 'test' ? 'test' : 'development';

const rawApiUrl =
  (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_BASE_URL) || 'http://localhost:8000';
const apiBaseUrl = normalizeApiUrl(rawApiUrl);
const apiV1Url = `${apiBaseUrl}/api/v1`;

export const config: AppConfig = Object.freeze({
  apiBaseUrl,
  apiV1Url,
  environment,
  isProduction: environment === 'production',
  isDevelopment: environment === 'development',
  isTest: environment === 'test',
  queryClient: {
    staleTimeMs: 1000 * 60 * 2, // 2 minutes
    retryCount: 1,
    timeoutMs: 15000,
  },
  limits: {
    minTextLength: 1,
    maxTextLength: 2500,
    defaultSpeechRate: 1.0,
    defaultPitch: 1.0,
  },
});
