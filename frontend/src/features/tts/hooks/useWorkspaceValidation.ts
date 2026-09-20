import { useMemo } from 'react';
import { validateWorkspace } from '../utils/textValidation';
import { WorkspaceValidationResult } from '../types/tts.types';
import { Voice } from '../../../types';
import { config as appConfig } from '../../../app/config';

export function useWorkspaceValidation(
  text: string,
  languageCode: string | null,
  voiceId: string | null,
  voices: Voice[] = [],
  maxCharacters: number = appConfig.limits.maxTextLength
): WorkspaceValidationResult {
  return useMemo(() => {
    return validateWorkspace(text, languageCode, voiceId, voices, maxCharacters);
  }, [text, languageCode, voiceId, voices, maxCharacters]);
}
