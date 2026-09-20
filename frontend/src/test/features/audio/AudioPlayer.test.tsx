import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { AudioPlayer } from '../../../features/audio/components/AudioPlayer';
import { AudioControls } from '../../../features/audio/components/AudioControls';
import { AudioProgress } from '../../../features/audio/components/AudioProgress';
import { VolumeControl } from '../../../features/audio/components/VolumeControl';
import { AudioDownloadButton } from '../../../features/audio/components/AudioDownloadButton';
import { TTSResponse } from '../../../types';

describe('Audio Player & Controls (Prompt 20)', () => {
  const mockTTSResponse: TTSResponse = {
    generation_id: 42,
    audio_url: '/api/v1/tts/audio/speech-42.mp3',
    download_url: '/api/v1/tts/download/speech-42.mp3',
    text: 'Quantum artificial intelligence transforms voice synthesis.',
    char_count: 59,
    word_count: 7,
    language: 'en-US',
    voice_id: 'voice-alpha',
    voice_name: 'Alpha Voice',
    duration_seconds: 4.8,
    provider: 'orchestrator',
    is_simulation: false,
    audio_format: 'mp3',
    content_type: 'audio/mpeg',
  };

  beforeEach(() => {
    window.HTMLMediaElement.prototype.play = vi.fn().mockResolvedValue(undefined);
    window.HTMLMediaElement.prototype.pause = vi.fn();
    window.HTMLMediaElement.prototype.load = vi.fn();
  });

  describe('AudioPlayer Component', () => {
    it('renders empty state when no audio source or result is supplied', () => {
      render(<AudioPlayer source={null} result={null} />);

      expect(screen.getByText(/no generated speech yet/i)).toBeInTheDocument();
      expect(screen.getByText(/type text in the workspace/i)).toBeInTheDocument();
    });

    it('renders active audio player when TTSResponse is provided', () => {
      render(<AudioPlayer result={mockTTSResponse} />);

      expect(screen.getByRole('region', { name: /bloop audio player/i })).toBeInTheDocument();
      expect(screen.getAllByText('Alpha Voice')[0]).toBeInTheDocument();
      expect(screen.getByText(/~4.8s/)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /play generated speech/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /download generated audio file/i })).toBeInTheDocument();
    });

    it('shows text divergence warning if workspace text differs from synthesized text', () => {
      render(
        <AudioPlayer
          result={mockTTSResponse}
          currentText="New divergent text entered by the user in the workspace."
        />
      );

      expect(
        screen.getByText(/workspace text has changed since this audio was synthesized/i)
      ).toBeInTheDocument();
    });

    it('does not show text divergence warning if workspace text matches synthesized text', () => {
      render(
        <AudioPlayer
          result={mockTTSResponse}
          currentText="Quantum artificial intelligence transforms voice synthesis."
        />
      );

      expect(
        screen.queryByText(/workspace text has changed since this audio was synthesized/i)
      ).not.toBeInTheDocument();
    });
  });

  describe('AudioControls Component', () => {
    it('renders accessible play/pause and relative seek controls', () => {
      const handleToggle = vi.fn();
      const handleRestart = vi.fn();
      const handleSeekRel = vi.fn();

      render(
        <AudioControls
          status="ready"
          isPlaying={false}
          isEnded={false}
          isLoading={false}
          onTogglePlay={handleToggle}
          onRestart={handleRestart}
          onSeekRelative={handleSeekRel}
        />
      );

      const playBtn = screen.getByRole('button', { name: /play generated speech/i });
      fireEvent.click(playBtn);
      expect(handleToggle).toHaveBeenCalledTimes(1);

      const rewindBtn = screen.getByRole('button', { name: /rewind 5 seconds/i });
      fireEvent.click(rewindBtn);
      expect(handleSeekRel).toHaveBeenCalledWith(-5);

      const fwdBtn = screen.getByRole('button', { name: /forward 5 seconds/i });
      fireEvent.click(fwdBtn);
      expect(handleSeekRel).toHaveBeenCalledWith(5);
    });

    it('renders replay button when audio has ended', () => {
      const handleRestart = vi.fn();
      render(
        <AudioControls
          status="ended"
          isPlaying={false}
          isEnded={true}
          isLoading={false}
          onTogglePlay={vi.fn()}
          onRestart={handleRestart}
        />
      );

      const replayBtn = screen.getByRole('button', { name: /replay generated speech/i });
      expect(replayBtn).toBeInTheDocument();
      fireEvent.click(replayBtn);
      expect(handleRestart).toHaveBeenCalledTimes(1);
    });
  });

  describe('AudioProgress Component', () => {
    it('displays formatted elapsed time and duration with accessible ARIA attributes', () => {
      const handleSeek = vi.fn();
      render(
        <AudioProgress
          currentTime={65}
          duration={125}
          bufferedProgress={50}
          onSeek={handleSeek}
        />
      );

      expect(screen.getByText('01:05')).toBeInTheDocument();
      expect(screen.getByText('02:05')).toBeInTheDocument();

      const slider = screen.getByRole('slider', { name: /seek audio playback/i });
      expect(slider).toBeInTheDocument();
      expect(slider).toHaveAttribute('aria-valuenow', '65');
      expect(slider).toHaveAttribute('aria-valuemax', '125');

      fireEvent.change(slider, { target: { value: '80' } });
      expect(handleSeek).toHaveBeenCalledWith(80);
    });
  });

  describe('VolumeControl Component', () => {
    it('toggles mute and updates volume slider', () => {
      const handleVol = vi.fn();
      const handleMute = vi.fn();

      render(
        <VolumeControl
          volume={0.8}
          isMuted={false}
          onVolumeChange={handleVol}
          onToggleMute={handleMute}
        />
      );

      const muteBtn = screen.getByRole('button', { name: /mute audio/i });
      fireEvent.click(muteBtn);
      expect(handleMute).toHaveBeenCalledTimes(1);

      const volSlider = screen.getByRole('slider', { name: /adjust volume/i });
      fireEvent.change(volSlider, { target: { value: '0.4' } });
      expect(handleVol).toHaveBeenCalledWith(0.4);
    });
  });

  describe('AudioDownloadButton Component', () => {
    it('renders download button and handles click', () => {
      render(
        <AudioDownloadButton
          downloadUrl="/api/v1/tts/download/test.mp3"
          generationId={42}
          voiceName="Alpha"
          audioFormat="mp3"
        />
      );

      const dlBtn = screen.getByRole('button', { name: /download generated audio file/i });
      expect(dlBtn).toBeInTheDocument();
      expect(dlBtn).toHaveTextContent(/download/i);
    });
  });
});
