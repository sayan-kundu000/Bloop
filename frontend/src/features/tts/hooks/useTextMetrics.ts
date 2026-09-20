import { useMemo } from 'react';
import { calculateTextMetrics } from '../utils/textMetrics';
import { TextMetricsData } from '../types/tts.types';
import { config as appConfig } from '../../../app/config';

export function useTextMetrics(
  text: string,
  maxCharacters: number = appConfig.limits.maxTextLength,
  speed: number = 1.0
): TextMetricsData {
  return useMemo(() => {
    return calculateTextMetrics(text, maxCharacters, speed);
  }, [text, maxCharacters, speed]);
}
