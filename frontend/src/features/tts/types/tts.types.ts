import { Language, Voice } from '../../../types';

export interface TTSWorkspaceState {
  text: string;
  languageCode: string | null;
  voiceId: string | null;
  speed: number;
  pitch: number;
  emotion: string;
}

export interface TextMetricsData {
  characterCount: number;
  wordCount: number;
  estimatedDurationSeconds: number;
  maxCharacters: number;
  isNearLimit: boolean;
  isAtLimit: boolean;
  isOverLimit: boolean;
  percentageUsed: number;
}

export type ValidationErrorCode =
  | 'TEXT_EMPTY'
  | 'TEXT_TOO_LONG'
  | 'MISSING_LANGUAGE'
  | 'MISSING_VOICE'
  | 'VOICE_LANGUAGE_MISMATCH'
  | null;

export interface WorkspaceValidationResult {
  isValid: boolean;
  isEmpty: boolean;
  isOverLimit: boolean;
  error: string | null;
  code: ValidationErrorCode;
  canGenerate: boolean;
}

export interface TTSGenerationPayload {
  text: string;
  language: string;
  voice_id: string;
  speed?: number;
  pitch?: number;
  emotion?: string;
}

export interface PresetSample {
  id: string;
  label: string;
  text: string;
  description?: string;
}

export type GenerationLifecycleStatus =
  | 'idle'
  | 'ready'
  | 'generating'
  | 'success'
  | 'error';

export interface TTSGenerationOptions {
  onSuccess?: (data: import('../../../types').TTSResponse) => void;
  onError?: (error: import('../../../lib/api/errors').FrontendApiError) => void;
}
