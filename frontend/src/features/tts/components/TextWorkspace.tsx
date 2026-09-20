import React, { useEffect, useMemo, useState } from 'react';
import { TextEditor } from './TextEditor';
import { TextMetrics } from './TextMetrics';
import { TextValidationMessage } from './TextValidationMessage';
import { WorkspaceToolbar } from './WorkspaceToolbar';
import { WorkspaceEmptyState } from './WorkspaceEmptyState';
import { LanguageSelector } from './LanguageSelector';
import { VoiceSelector } from './VoiceSelector';
import { SelectionSummary } from './SelectionSummary';
import { GenerationControls } from './GenerationControls';

import { useLanguages } from '../hooks/useLanguages';
import { useVoices } from '../hooks/useVoices';
import { useTextMetrics } from '../hooks/useTextMetrics';
import { useWorkspaceValidation } from '../hooks/useWorkspaceValidation';
import { useTTSGeneration } from '../hooks/useTTSGeneration';
import { isVoiceCompatibleWithLanguage } from '../utils/textValidation';
import { TTSGenerationPayload } from '../types/tts.types';
import { TTSResponse } from '../../../types';
import { useWorkspaceStore } from '../../../stores/workspaceStore';
import { config as appConfig } from '../../../app/config';

import { useAuthStore } from '../../../stores/authStore';
import { userApi } from '../../../api/client';
import { useQuery } from '@tanstack/react-query';

export interface TextWorkspaceProps {
  onGenerate?: (payload: TTSGenerationPayload) => void;
  onSuccess?: (result: TTSResponse) => void;
  isGenerating?: boolean;
  externalResult?: TTSResponse | null;
  externalError?: string | null;
  onDismissError?: () => void;
  onPlayResult?: (url: string, title: string) => void;
}

export const TextWorkspace: React.FC<TextWorkspaceProps> = ({
  onGenerate,
  onSuccess,
  isGenerating: externalIsGenerating,
  externalResult,
  externalError,
  onDismissError,
  onPlayResult,
}) => {
  const {
    text,
    languageCode,
    voiceId,
    speed,
    pitch,
    emotion,
    setText,
    setLanguageCode,
    setVoiceId,
    clearText,
    loadSample,
  } = useWorkspaceStore();

  const maxCharacters = appConfig.limits.maxTextLength;
  const { isAuthenticated } = useAuthStore();

  // Load user preferences when authenticated for initial state defaults
  const { data: userPreferences } = useQuery({
    queryKey: ['user-preferences'],
    queryFn: userApi.getPreferences,
    enabled: isAuthenticated,
    staleTime: 1000 * 60 * 5,
    refetchOnWindowFocus: false,
  });

  const [preferencesApplied, setPreferencesApplied] = useState(false);

  // Internal TanStack Query mutation hook for self-contained operation
  const internalGeneration = useTTSGeneration({
    onSuccess: (data) => {
      if (onSuccess) {
        onSuccess(data);
      }
    },
  });

  // TanStack Query hooks for dynamic language and voice catalogs
  const {
    languages,
    isLoading: isLoadingLanguages,
    isError: isErrorLanguages,
    refetch: refetchLanguages,
  } = useLanguages();

  const {
    voices,
    isLoading: isLoadingVoices,
    isError: isErrorVoices,
    refetch: refetchVoices,
  } = useVoices(languageCode);

  // Compute live metrics and validation
  const metrics = useTextMetrics(text, maxCharacters, speed);
  const validation = useWorkspaceValidation(text, languageCode, voiceId, voices, maxCharacters);

  // Resolve currently active objects for display
  const activeLanguage = useMemo(() => {
    return languages.find((l) => l.code === languageCode) || null;
  }, [languages, languageCode]);

  const activeVoice = useMemo(() => {
    return voices.find((v) => v.voice_id === voiceId) || null;
  }, [voices, voiceId]);

  const isVoiceCompatible = useMemo(() => {
    if (!activeVoice || !languageCode) return false;
    return isVoiceCompatibleWithLanguage(activeVoice, languageCode);
  }, [activeVoice, languageCode]);

  // Determine effective generation state (external vs internal)
  const isGenerating = externalIsGenerating !== undefined ? externalIsGenerating : internalGeneration.isPending;
  const activeResult = externalResult !== undefined ? externalResult : internalGeneration.data;
  const activeErrorMessage = externalError !== undefined ? externalError : internalGeneration.friendlyError;
  const isError = Boolean(activeErrorMessage);
  const isRetryable = externalError !== undefined ? true : internalGeneration.isRetryable;

  // Preference initialization: apply user saved preferred language & voice if available and valid
  useEffect(() => {
    if (preferencesApplied || !userPreferences) return;

    if (userPreferences.default_language_code && languages.length > 0) {
      const matchingLang = languages.find((l) => l.code === userPreferences.default_language_code);
      if (matchingLang) {
        setLanguageCode(matchingLang.code);
      }
    }

    if (userPreferences.default_voice_id && voices.length > 0) {
      const matchingVoice = voices.find(
        (v) =>
          v.voice_id === userPreferences.default_voice_id &&
          (!languageCode || isVoiceCompatibleWithLanguage(v, languageCode))
      );
      if (matchingVoice) {
        setVoiceId(matchingVoice.voice_id);
      }
    }

    setPreferencesApplied(true);
  }, [userPreferences, languages, voices, languageCode, preferencesApplied, setLanguageCode, setVoiceId]);

  // If initial language is unselected and languages load, initialize with the first active language
  useEffect(() => {
    if (!languageCode && languages.length > 0) {
      setLanguageCode(languages[0].code);
    }
  }, [languages, languageCode, setLanguageCode]);

  // Reactive safeguard: ensure selected voice remains valid whenever language or voice catalog updates
  useEffect(() => {
    if (voiceId && languageCode && voices.length > 0 && !isLoadingVoices) {
      const currentVoice = voices.find((v) => v.voice_id === voiceId);
      if (!currentVoice || !isVoiceCompatibleWithLanguage(currentVoice, languageCode)) {
        setVoiceId('');
      }
    }
  }, [languageCode, voiceId, voices, isLoadingVoices, setVoiceId]);

  // Handle language change with incompatible voice clearing
  const handleSelectLanguage = (newLanguageCode: string) => {
    setLanguageCode(newLanguageCode);

    // If a voice is currently selected, check if it remains compatible with the new language
    if (activeVoice && !isVoiceCompatibleWithLanguage(activeVoice, newLanguageCode)) {
      setVoiceId('');
    }
  };

  const handleSelectVoice = (newVoiceId: string) => {
    setVoiceId(newVoiceId);
  };

  /**
   * Constructs payload from validated workspace state and dispatches generation
   */
  const handleGenerate = () => {
    if (!validation.canGenerate || isGenerating || !languageCode || !voiceId) {
      return;
    }

    const payload: TTSGenerationPayload = {
      text,
      language: languageCode,
      voice_id: voiceId,
      speed,
      pitch,
      emotion,
    };

    if (onGenerate) {
      onGenerate(payload);
    } else {
      internalGeneration.mutate(payload);
    }
  };

  /**
   * Retries synthesis with the current validated workspace inputs
   */
  const handleRetry = () => {
    if (!validation.canGenerate || isGenerating || !languageCode || !voiceId) {
      return;
    }

    const currentPayload: TTSGenerationPayload = {
      text,
      language: languageCode,
      voice_id: voiceId,
      speed,
      pitch,
      emotion,
    };

    if (onGenerate) {
      onGenerate(currentPayload);
    } else {
      internalGeneration.retry(currentPayload);
    }
  };

  const handleDismissError = () => {
    if (onDismissError) {
      onDismissError();
    }
    if (internalGeneration.reset) {
      internalGeneration.reset();
    }
  };

  const readinessHint = useMemo(() => {
    if (!validation.isValid) {
      return 'Please provide valid speech text to enable synthesis.';
    }
    if (!languageCode) {
      return 'Please select a language locale.';
    }
    if (!voiceId) {
      return 'Please select a compatible voice from the dynamic catalog.';
    }
    if (!isVoiceCompatible) {
      return 'Selected voice is not compatible with current language.';
    }
    return 'Ready to synthesize speech';
  }, [validation.isValid, languageCode, voiceId, isVoiceCompatible]);

  return (
    <div className="glass-panel rounded-2xl p-5 sm:p-6 border border-white/10 shadow-2xl space-y-6">
      {/* 1. Workspace Toolbar */}
      <WorkspaceToolbar
        hasText={text.length > 0}
        textLength={text.length}
        onClear={clearText}
        onLoadSample={loadSample}
        onPaste={(pasted) => setText(pasted)}
        disabled={isGenerating}
      />

      {/* 2. Main Text Editor */}
      <div className="space-y-2">
        <TextEditor
          text={text}
          onChange={setText}
          isOverLimit={metrics.isOverLimit}
          disabled={isGenerating}
        />

        {/* 3. Text Metrics Bar */}
        <TextMetrics metrics={metrics} />
      </div>

      {/* 4. Empty State Notice */}
      {text.length === 0 && (
        <WorkspaceEmptyState
          onLoadDefaultSample={() => loadSample(appConfig.limits.minTextLength ? 'Hello, welcome to Bloop.' : '')}
        />
      )}

      {/* 5. Dynamic Selectors Grid (Responsive Layout) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2 border-t border-white/5">
        <LanguageSelector
          languages={languages}
          selectedLanguageCode={languageCode}
          onSelectLanguage={handleSelectLanguage}
          isLoading={isLoadingLanguages}
          isError={isErrorLanguages}
          onRetry={refetchLanguages}
          disabled={isGenerating}
        />

        <VoiceSelector
          voices={voices}
          selectedVoiceId={voiceId}
          selectedLanguageCode={languageCode}
          onSelectVoice={handleSelectVoice}
          isLoading={isLoadingVoices}
          isError={isErrorVoices}
          onRetry={refetchVoices}
          disabled={isGenerating}
        />
      </div>

      {/* 6. Selection Summary */}
      <SelectionSummary
        language={activeLanguage}
        voice={activeVoice}
        isCompatible={isVoiceCompatible}
      />

      {/* 7. Validation Feedback Alert */}
      <TextValidationMessage validation={validation} />

      {/* 8. Generation Controls: Status, Error, Success & Generate Action */}
      <GenerationControls
        canGenerate={validation.canGenerate}
        isGenerating={isGenerating}
        onGenerate={handleGenerate}
        isError={isError}
        errorMessage={activeErrorMessage}
        isRetryable={isRetryable}
        onRetry={handleRetry}
        onDismissError={handleDismissError}
        result={activeResult}
        currentText={text}
        voiceName={activeVoice?.name}
        languageCode={languageCode}
        onPlayResult={onPlayResult}
        readinessHint={readinessHint}
      />
    </div>
  );
};
