import { TextMetricsData } from '../types/tts.types';

/**
 * Deterministically counts characters in the text string without modification.
 */
export function countCharacters(text: string): number {
  return typeof text === 'string' ? text.length : 0;
}

/**
 * Deterministically counts words in a text string.
 * Handles empty strings, consecutive spaces, tabs, newlines, and Unicode text
 * without counting whitespace as words.
 */
export function countWords(text: string): number {
  if (!text || typeof text !== 'string') {
    return 0;
  }
  const trimmed = text.trim();
  if (trimmed.length === 0) {
    return 0;
  }
  // Split on one or more whitespace characters (spaces, tabs, newlines)
  const tokens = trimmed.split(/\s+/);
  return tokens.length;
}

/**
 * Estimates speech duration in seconds based on a conversational ~150 words-per-minute (2.5 words/sec)
 * baseline, adjusted for the selected speech playback speed.
 */
export function estimateDurationSeconds(wordCount: number, speed: number = 1.0): number {
  if (wordCount <= 0) {
    return 0;
  }
  const effectiveSpeed = speed > 0 ? speed : 1.0;
  const rawSeconds = wordCount / (2.5 * effectiveSpeed);
  // Round to one decimal place
  return Math.round(rawSeconds * 10) / 10;
}

/**
 * Calculates complete text metrics given a text string, character maximum, and speed.
 */
export function calculateTextMetrics(
  text: string,
  maxCharacters: number = 2500,
  speed: number = 1.0
): TextMetricsData {
  const characterCount = countCharacters(text);
  const wordCount = countWords(text);
  const estimatedDurationSeconds = estimateDurationSeconds(wordCount, speed);
  const isOverLimit = characterCount > maxCharacters;
  const isAtLimit = characterCount === maxCharacters;
  const percentageUsed = maxCharacters > 0 ? Math.min((characterCount / maxCharacters) * 100, 100) : 0;
  const isNearLimit = percentageUsed >= 85 && !isOverLimit;

  return {
    characterCount,
    wordCount,
    estimatedDurationSeconds,
    maxCharacters,
    isNearLimit,
    isAtLimit,
    isOverLimit,
    percentageUsed,
  };
}
