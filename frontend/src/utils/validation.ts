/**
 * Text-to-Speech validation rules and live metrics.
 */

export const TTS_LIMITS = {
  MIN_LENGTH: 1,
  MAX_LENGTH: 2500,
  WARN_THRESHOLD: 2400,
};

export interface TextMetrics {
  charCount: number;
  wordCount: number;
  estimatedDurationSeconds: number;
  isValid: boolean;
  error?: string;
}

export function validateAndCalculateMetrics(text: string): TextMetrics {
  const trimmed = text.trim();
  const charCount = trimmed.length;
  const words = trimmed ? trimmed.split(/\s+/).filter(Boolean) : [];
  const wordCount = words.length;

  // Average reading speech rate: ~150 words per minute (2.5 words per second)
  const estimatedDurationSeconds = wordCount > 0 ? parseFloat((wordCount / 2.5).toFixed(1)) : 0;

  if (charCount === 0) {
    return {
      charCount: 0,
      wordCount: 0,
      estimatedDurationSeconds: 0,
      isValid: false,
      error: 'Text cannot be empty or whitespace only.',
    };
  }

  if (charCount > TTS_LIMITS.MAX_LENGTH) {
    return {
      charCount,
      wordCount,
      estimatedDurationSeconds,
      isValid: false,
      error: `Text length (${charCount}) exceeds maximum limit of ${TTS_LIMITS.MAX_LENGTH} characters.`,
    };
  }

  return {
    charCount,
    wordCount,
    estimatedDurationSeconds,
    isValid: true,
  };
}
