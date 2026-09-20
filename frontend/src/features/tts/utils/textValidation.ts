import { Voice } from '../../../types';
import { WorkspaceValidationResult, ValidationErrorCode } from '../types/tts.types';

/**
 * Checks whether a given voice supports a specific language locale code.
 */
export function isVoiceCompatibleWithLanguage(voice?: Voice | null, languageCode?: string | null): boolean {
  if (!voice || !languageCode) {
    return false;
  }
  // If the voice lists explicit supported languages (combining primary and M2M capabilities)
  if (Array.isArray(voice.supported_languages) && voice.supported_languages.length > 0) {
    if (voice.supported_languages.includes(languageCode)) {
      return true;
    }
  }
  // Primary language fallback
  return voice.language_code === languageCode;
}

/**
 * Evaluates text workspace validation rules and generation readiness.
 */
export function validateWorkspace(
  text: string,
  languageCode: string | null,
  voiceId: string | null,
  voices: Voice[] = [],
  maxCharacters: number = 2500
): WorkspaceValidationResult {
  const trimmed = typeof text === 'string' ? text.trim() : '';
  const isEmpty = trimmed.length === 0;
  const isOverLimit = (typeof text === 'string' ? text.length : 0) > maxCharacters;

  let error: string | null = null;
  let code: ValidationErrorCode = null;

  // Check 1: Empty text
  if (isEmpty) {
    error = 'Please enter some text before generating speech.';
    code = 'TEXT_EMPTY';
  }
  // Check 2: Text exceeds maximum limit
  else if (isOverLimit) {
    error = `Text exceeds the maximum allowed limit of ${maxCharacters.toLocaleString()} characters. Please shorten your text.`;
    code = 'TEXT_TOO_LONG';
  }
  // Check 3: Language must be selected
  else if (!languageCode) {
    error = 'Please select a language.';
    code = 'MISSING_LANGUAGE';
  }
  // Check 4: Voice must be selected
  else if (!voiceId) {
    error = 'Please select a voice.';
    code = 'MISSING_VOICE';
  }
  // Check 5: Selected voice must support selected language
  else {
    const selectedVoice = voices.find((v) => v.voice_id === voiceId);
    if (selectedVoice && !isVoiceCompatibleWithLanguage(selectedVoice, languageCode)) {
      error = `The selected voice '${selectedVoice.name}' is not compatible with language '${languageCode}'.`;
      code = 'VOICE_LANGUAGE_MISMATCH';
    }
  }

  const isValid = !isEmpty && !isOverLimit;
  const canGenerate = isValid && !!languageCode && !!voiceId && code === null;

  return {
    isValid,
    isEmpty,
    isOverLimit,
    error,
    code,
    canGenerate,
  };
}
