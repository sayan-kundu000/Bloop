import { describe, it, expect } from 'vitest';
import {
  validateWorkspace,
  isVoiceCompatibleWithLanguage,
} from '../../../features/tts/utils/textValidation';
import { Voice } from '../../../types';

describe('Text Validation & Voice Compatibility Utilities', () => {
  const mockVoices: Voice[] = [
    {
      id: 1,
      voice_id: 'voice-en-us',
      name: 'English Studio Voice',
      language_code: 'en-US',
      supported_languages: ['en-US', 'en-GB'],
      gender: 'neutral',
      provider: 'dynamic',
      is_active: true,
      is_user_configured: false,
    },
    {
      id: 2,
      voice_id: 'voice-es-es',
      name: 'Spanish Studio Voice',
      language_code: 'es-ES',
      supported_languages: ['es-ES'],
      gender: 'female',
      provider: 'dynamic',
      is_active: true,
      is_user_configured: false,
    },
  ];

  describe('isVoiceCompatibleWithLanguage', () => {
    it('returns true when voice matches primary language code', () => {
      expect(isVoiceCompatibleWithLanguage(mockVoices[0], 'en-US')).toBe(true);
    });

    it('returns true when language is in supported_languages list', () => {
      expect(isVoiceCompatibleWithLanguage(mockVoices[0], 'en-GB')).toBe(true);
    });

    it('returns false when language is not supported by the voice', () => {
      expect(isVoiceCompatibleWithLanguage(mockVoices[0], 'fr-FR')).toBe(false);
      expect(isVoiceCompatibleWithLanguage(mockVoices[1], 'en-US')).toBe(false);
    });

    it('handles null or undefined inputs gracefully', () => {
      expect(isVoiceCompatibleWithLanguage(null, 'en-US')).toBe(false);
      expect(isVoiceCompatibleWithLanguage(mockVoices[0], null)).toBe(false);
    });
  });

  describe('validateWorkspace', () => {
    it('returns TEXT_EMPTY error when text is empty or whitespace only', () => {
      const resultEmpty = validateWorkspace('', 'en-US', 'voice-en-us', mockVoices, 2500);
      expect(resultEmpty.isValid).toBe(false);
      expect(resultEmpty.isEmpty).toBe(true);
      expect(resultEmpty.code).toBe('TEXT_EMPTY');
      expect(resultEmpty.canGenerate).toBe(false);

      const resultWhitespace = validateWorkspace('   \n  ', 'en-US', 'voice-en-us', mockVoices, 2500);
      expect(resultWhitespace.code).toBe('TEXT_EMPTY');
    });

    it('returns TEXT_TOO_LONG error when text length exceeds limit', () => {
      const overLimitText = 'a'.repeat(2505);
      const result = validateWorkspace(overLimitText, 'en-US', 'voice-en-us', mockVoices, 2500);
      expect(result.isValid).toBe(false);
      expect(result.isOverLimit).toBe(true);
      expect(result.code).toBe('TEXT_TOO_LONG');
      expect(result.canGenerate).toBe(false);
    });

    it('returns MISSING_LANGUAGE when no language is selected', () => {
      const result = validateWorkspace('Hello world', null, 'voice-en-us', mockVoices, 2500);
      expect(result.code).toBe('MISSING_LANGUAGE');
      expect(result.canGenerate).toBe(false);
    });

    it('returns MISSING_VOICE when no voice is selected', () => {
      const result = validateWorkspace('Hello world', 'en-US', null, mockVoices, 2500);
      expect(result.code).toBe('MISSING_VOICE');
      expect(result.canGenerate).toBe(false);
    });

    it('returns VOICE_LANGUAGE_MISMATCH when selected voice does not support selected language', () => {
      // voice-es-es does not support en-US
      const result = validateWorkspace('Hello world', 'en-US', 'voice-es-es', mockVoices, 2500);
      expect(result.code).toBe('VOICE_LANGUAGE_MISMATCH');
      expect(result.canGenerate).toBe(false);
    });

    it('returns canGenerate: true when text, language, and compatible voice are valid', () => {
      const result = validateWorkspace('Hello world', 'en-US', 'voice-en-us', mockVoices, 2500);
      expect(result.isValid).toBe(true);
      expect(result.isEmpty).toBe(false);
      expect(result.isOverLimit).toBe(false);
      expect(result.code).toBeNull();
      expect(result.error).toBeNull();
      expect(result.canGenerate).toBe(true);
    });
  });
});
