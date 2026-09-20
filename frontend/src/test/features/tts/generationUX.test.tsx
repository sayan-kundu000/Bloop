import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { GenerateButton } from '../../../features/tts/components/GenerateButton';
import { GenerationStatus } from '../../../features/tts/components/GenerationStatus';
import { GenerationError } from '../../../features/tts/components/GenerationError';
import { GenerationSuccess } from '../../../features/tts/components/GenerationSuccess';
import { RetryGenerationButton } from '../../../features/tts/components/RetryGenerationButton';
import { GenerationControls } from '../../../features/tts/components/GenerationControls';
import { TTSResponse } from '../../../types';

const mockResponse: TTSResponse = {
  generation_id: 101,
  audio_url: '/api/v1/tts/audio/test.mp3',
  download_url: '/api/v1/tts/download/test.mp3',
  text: 'Synthesized speech content sample',
  char_count: 34,
  word_count: 4,
  language: 'en-US',
  voice_id: 'voice-studio-alpha',
  voice_name: 'Studio Alpha',
  duration_seconds: 2.5,
  provider: 'dynamic-orchestrator',
  is_simulation: false,
  audio_format: 'mp3',
  content_type: 'audio/mpeg',
};

describe('Speech Generation UX Components', () => {
  describe('GenerateButton', () => {
    it('renders idle state with accessible label', () => {
      const handleClick = vi.fn();
      render(<GenerateButton onClick={handleClick} />);

      const button = screen.getByRole('button', { name: /generate speech/i });
      expect(button).toBeInTheDocument();
      expect(button).not.toBeDisabled();
      expect(button).toHaveAttribute('aria-busy', 'false');

      fireEvent.click(button);
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('renders generating loading state with aria-busy and prevents extra clicks', () => {
      const handleClick = vi.fn();
      render(<GenerateButton onClick={handleClick} isGenerating={true} />);

      const button = screen.getByRole('button', { name: /generating speech/i });
      expect(button).toBeInTheDocument();
      expect(button).toHaveAttribute('aria-busy', 'true');
      expect(screen.getByText(/generating…/i)).toBeInTheDocument();

      fireEvent.click(button);
      expect(handleClick).not.toHaveBeenCalled();
    });

    it('respects disabled prop and prevents clicks', () => {
      const handleClick = vi.fn();
      render(<GenerateButton onClick={handleClick} disabled={true} />);

      const button = screen.getByRole('button', { name: /generate speech/i });
      expect(button).toBeDisabled();

      fireEvent.click(button);
      expect(handleClick).not.toHaveBeenCalled();
    });
  });

  describe('GenerationStatus (Indeterminate Loading Invariant)', () => {
    it('renders accessible live region when generating', () => {
      render(
        <GenerationStatus
          isGenerating={true}
          voiceName="Dynamic Aura"
          languageCode="en-US"
        />
      );

      const status = screen.getByRole('status');
      expect(status).toBeInTheDocument();
      expect(status).toHaveAttribute('aria-live', 'polite');
      expect(status).toHaveAttribute('aria-busy', 'true');
      expect(screen.getByText(/generating speech…/i)).toBeInTheDocument();
      expect(screen.getByText(/dynamic aura/i)).toBeInTheDocument();
    });

    it('strictly contains no simulated fake percentages (Prompt 19 Invariant)', () => {
      const { container } = render(
        <GenerationStatus
          isGenerating={true}
          voiceName="Dynamic Aura"
          languageCode="en-US"
        />
      );

      // Verify no percentage strings like "47%", "84%" appear in the DOM
      expect(container.textContent).not.toMatch(/\d+%/);
    });

    it('renders nothing when not generating', () => {
      const { container } = render(<GenerationStatus isGenerating={false} />);
      expect(container.firstChild).toBeNull();
    });
  });

  describe('GenerationError & Retry', () => {
    it('renders alert landmark with friendly error message', () => {
      render(
        <GenerationError
          error="The selected voice is not available for this language."
          isRetryable={false}
        />
      );

      const alert = screen.getByRole('alert');
      expect(alert).toBeInTheDocument();
      expect(alert).toHaveAttribute('aria-live', 'assertive');
      expect(
        screen.getByText('The selected voice is not available for this language.')
      ).toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /retry/i })).not.toBeInTheDocument();
    });

    it('renders RetryGenerationButton when error is retryable and triggers onRetry', () => {
      const handleRetry = vi.fn();
      render(
        <GenerationError
          error="Speech generation took too long. Please try again."
          isRetryable={true}
          onRetry={handleRetry}
        />
      );

      const retryButton = screen.getByRole('button', { name: /retry/i });
      expect(retryButton).toBeInTheDocument();

      fireEvent.click(retryButton);
      expect(handleRetry).toHaveBeenCalledTimes(1);
    });

    it('triggers dismiss callback when dismiss button is clicked', () => {
      const handleDismiss = vi.fn();
      render(
        <GenerationError
          error="A temporary glitch occurred."
          onDismiss={handleDismiss}
        />
      );

      const dismissButton = screen.getByLabelText(/dismiss error/i);
      fireEvent.click(dismissButton);
      expect(handleDismiss).toHaveBeenCalledTimes(1);
    });
  });

  describe('GenerationSuccess & Prompt 20 Handoff', () => {
    it('renders synthesis confirmation and metadata summary', () => {
      render(<GenerationSuccess result={mockResponse} />);

      expect(screen.getByText(/speech generated successfully/i)).toBeInTheDocument();
      expect(screen.getAllByText('Studio Alpha')[0]).toBeInTheDocument();
      expect(screen.getAllByText(/~2.5s/)[0]).toBeInTheDocument();
      expect(screen.getByText(/34 chars/)).toBeInTheDocument();
      expect(screen.getAllByText('MP3')[0]).toBeInTheDocument();

      // Verify Prompt 20 handoff container
      const handoff = document.getElementById('tts-audio-handoff-container');
      expect(handoff).toBeInTheDocument();
      expect(handoff).toHaveAttribute('data-generation-id', '101');
      expect(handoff).toHaveAttribute('data-audio-url', '/api/v1/tts/audio/test.mp3');
    });

    it('warns user if workspace text diverged since synthesis', () => {
      render(
        <GenerationSuccess
          result={mockResponse}
          currentText="New modified text that differs from synthesized"
        />
      );

      expect(
        screen.getAllByText(/workspace text has changed since this audio was synthesized/i)[0]
      ).toBeInTheDocument();
    });
  });

  describe('GenerationControls Orchestration', () => {
    it('coordinates generate, status, error, and success lifecycle states', () => {
      const handleGenerate = vi.fn();
      const handleRetry = vi.fn();

      const { rerender } = render(
        <GenerationControls
          canGenerate={true}
          isGenerating={false}
          onGenerate={handleGenerate}
          isError={false}
          errorMessage={null}
          isRetryable={false}
          onRetry={handleRetry}
          result={null}
        />
      );

      expect(screen.getByText(/ready to synthesize speech/i)).toBeInTheDocument();
      const generateBtn = screen.getByRole('button', { name: /generate speech/i });
      expect(generateBtn).not.toBeDisabled();

      fireEvent.click(generateBtn);
      expect(handleGenerate).toHaveBeenCalledTimes(1);

      // Transition to Generating
      rerender(
        <GenerationControls
          canGenerate={true}
          isGenerating={true}
          onGenerate={handleGenerate}
          isError={false}
          errorMessage={null}
          isRetryable={false}
          onRetry={handleRetry}
          result={null}
        />
      );

      expect(screen.getByRole('status')).toBeInTheDocument();

      // Transition to Success
      rerender(
        <GenerationControls
          canGenerate={true}
          isGenerating={false}
          onGenerate={handleGenerate}
          isError={false}
          errorMessage={null}
          isRetryable={false}
          onRetry={handleRetry}
          result={mockResponse}
        />
      );

      expect(screen.getByText(/speech generated successfully/i)).toBeInTheDocument();
    });
  });
});
