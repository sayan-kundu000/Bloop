/**
 * Text-to-Speech (TTS) Feature Module Barrel Export
 */

// Components
export { TextWorkspace } from './components/TextWorkspace';
export { TextEditor } from './components/TextEditor';
export { TextMetrics } from './components/TextMetrics';
export { TextValidationMessage } from './components/TextValidationMessage';
export { LanguageSelector } from './components/LanguageSelector';
export { VoiceSelector } from './components/VoiceSelector';
export { SelectionSummary } from './components/SelectionSummary';
export { WorkspaceToolbar } from './components/WorkspaceToolbar';
export { WorkspaceEmptyState } from './components/WorkspaceEmptyState';
export { GenerateButton } from './components/GenerateButton';
export { GenerationStatus } from './components/GenerationStatus';
export { GenerationError } from './components/GenerationError';
export { GenerationSuccess } from './components/GenerationSuccess';
export { RetryGenerationButton } from './components/RetryGenerationButton';
export { GenerationControls } from './components/GenerationControls';

// Hooks
export { useLanguages } from './hooks/useLanguages';
export { useVoices } from './hooks/useVoices';
export { useTextMetrics } from './hooks/useTextMetrics';
export { useWorkspaceValidation } from './hooks/useWorkspaceValidation';
export { useTTSGeneration } from './hooks/useTTSGeneration';

// Utilities
export {
  countCharacters,
  countWords,
  estimateDurationSeconds,
  calculateTextMetrics,
} from './utils/textMetrics';
export {
  validateWorkspace,
  isVoiceCompatibleWithLanguage,
} from './utils/textValidation';
export {
  getFriendlyTTSErrorMessage,
  isRetryableTTSError,
  TTS_ERROR_MESSAGE_MAP,
} from './utils/ttsErrorMapping';

// Types
export * from './types/tts.types';

// API
export { ttsFeatureApi } from './api/tts.api';
