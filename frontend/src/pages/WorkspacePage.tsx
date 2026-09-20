import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Sparkles, Volume2, Play, Download, AlertCircle, Wand2, Atom, Sliders, Film, Cpu, Smile } from 'lucide-react';
import { voiceApi, ttsApi } from '../api/client';
import { TextWorkspace } from '../features/tts';
import { getFriendlyTTSErrorMessage } from '../features/tts/utils/ttsErrorMapping';
import { AddVoiceModal } from '../components/tts/AddVoiceModal';
import { useWorkspaceStore } from '../stores/workspaceStore';
import { useAudioStore } from '../stores/audioStore';
import { TTSResponse, Voice } from '../types';
import { Link } from 'react-router-dom';
import { AudioPlayer } from '../features/audio';

export const WorkspacePage: React.FC = () => {
  const queryClient = useQueryClient();
  const { text, languageCode, voiceId, speed, pitch, emotion, stats, setSpeed, setPitch } = useWorkspaceStore();
  const { playAudio } = useAudioStore();

  const [isVoiceModalOpen, setIsVoiceModalOpen] = useState(false);
  const [latestAudio, setLatestAudio] = useState<TTSResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Fetch Languages
  const { data: languages = [], isLoading: isLoadingLangs } = useQuery({
    queryKey: ['languages'],
    queryFn: voiceApi.getLanguages,
  });

  // Fetch Voices (fetches complete dynamic catalog)
  const { data: voices = [], isLoading: isLoadingVoices } = useQuery({
    queryKey: ['voices'],
    queryFn: () => voiceApi.getVoices(),
  });

  // Speech Generation Mutation
  const generateMutation = useMutation({
    mutationFn: ttsApi.generateSpeech,
    onSuccess: (data) => {
      setLatestAudio(data);
      setErrorMessage(null);
      queryClient.invalidateQueries({ queryKey: ['history'] });
    },
    onError: (error: unknown) => {
      setErrorMessage(getFriendlyTTSErrorMessage(error));
    },
  });

  const handleGenerate = () => {
    if (!stats.is_valid) {
      setErrorMessage('Please enter valid text (1 to 2,500 characters).');
      return;
    }
    setErrorMessage(null);

    // Adapt language if the selected voice has a specific target locale
    const selectedVoice = voices.find((v) => v.voice_id === voiceId);
    const effectiveLanguage = selectedVoice?.language_code || languageCode;

    generateMutation.mutate({
      text,
      language: effectiveLanguage,
      voice_id: voiceId,
      speed,
      pitch,
      emotion,
    });
  };

  const handleVoiceSelect = (selectedVoice: Voice) => {
    if (selectedVoice.language_code && selectedVoice.language_code !== languageCode) {
      const hasLang = languages.some((l) => l.code === selectedVoice.language_code);
      if (hasLang) {
        useWorkspaceStore.getState().setLanguageCode(selectedVoice.language_code);
      }
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Page Header */}
      <div className="mb-8">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-extrabold text-white tracking-tight">
              Create <span className="gradient-text-bloop">Speech</span>
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Transform written words into rich, lifelike speech with dynamic voice orchestration.
            </p>
          </div>

          <Link
            to="/quantum"
            className="flex items-center space-x-2 px-3.5 py-1.5 rounded-xl bg-quantum-950/60 border border-quantum-500/30 text-quantum-300 hover:border-quantum-500/60 hover:text-white transition shadow-sm text-xs font-medium"
          >
            <Atom className="w-4 h-4 text-quantum-400 animate-spin-slow" />
            <span>Quantum Intelligence Lab</span>
          </Link>
        </div>
      </div>

      {/* Main Workspace Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Text Workspace (7 cols) */}
        <div className="lg:col-span-7 flex flex-col gap-6">
          <TextWorkspace
            onGenerate={(payload) => {
              setErrorMessage(null);
              generateMutation.mutate(payload);
            }}
            isGenerating={generateMutation.isPending}
            externalResult={latestAudio}
            externalError={errorMessage}
            onDismissError={() => setErrorMessage(null)}
            onPlayResult={(url, title) => playAudio(ttsApi.getAudioUrl(url), title)}
          />
        </div>

        {/* Right Column: Audio Output & Intelligent Insights (5 cols) */}
        <div className="lg:col-span-5 flex flex-col gap-6">
          {/* Latest Generated Audio Card */}
          <div className="glass-panel rounded-2xl p-6 border border-white/10 shadow-xl flex flex-col justify-between relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-bloop-500/10 rounded-full blur-3xl pointer-events-none" />

            <div>
              <div className="flex items-center justify-between border-b border-white/10 pb-3 mb-4">
                <div className="flex items-center space-x-2">
                  <Volume2 className="w-5 h-5 text-bloop-400" />
                  <h3 className="font-bold text-white text-base">Synthesized Audio Output</h3>
                </div>
                {latestAudio?.is_simulation && (
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30 font-mono">
                    Simulation Mode
                  </span>
                )}
              </div>

              {latestAudio ? (
                <div className="flex flex-col gap-4">
                  <div className="p-4 rounded-xl bg-slate-950/70 border border-white/10">
                    <p className="text-xs text-slate-400 mb-1">Generated Text Snippet:</p>
                    <p className="text-sm text-slate-200 line-clamp-3 italic">
                      "{latestAudio.text}"
                    </p>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-xs text-slate-300">
                    <div className="p-2.5 rounded-lg bg-slate-900/60 border border-white/5">
                      <span className="text-slate-400 block text-[11px]">Voice Used</span>
                      <span className="font-semibold text-white truncate block">
                        {latestAudio.voice_name || latestAudio.voice_id}
                      </span>
                    </div>
                    <div className="p-2.5 rounded-lg bg-slate-900/60 border border-white/5">
                      <span className="text-slate-400 block text-[11px]">Duration</span>
                      <span className="font-semibold text-white block">
                        ~{latestAudio.duration_seconds}s ({latestAudio.char_count} chars)
                      </span>
                    </div>
                  </div>

                  {/* Emotion Delivery Tone Indicator */}
                  {(latestAudio.emotion || emotion) && (
                    <div className="p-3 rounded-xl bg-slate-950/70 border border-bloop-500/20 flex items-center justify-between">
                      <div className="flex items-center space-x-2.5">
                        <div className="w-7 h-7 rounded-lg bg-bloop-500/20 border border-bloop-500/40 flex items-center justify-center text-bloop-400">
                          <Smile className="w-4 h-4" />
                        </div>
                        <div>
                          <span className="text-[10px] text-slate-400 block uppercase font-bold tracking-wider">
                            Active Emotion Delivery
                          </span>
                          <span className="text-xs font-semibold text-white">
                            {latestAudio.emotion || emotion}
                          </span>
                        </div>
                      </div>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-bloop-500/15 text-bloop-300 border border-bloop-500/30">
                        Inflected
                      </span>
                    </div>
                  )}

                  {/* Quantum-RAG Acoustic Resonance Badge */}
                  {latestAudio.quantum_metrics && (
                    <div className="p-4 rounded-xl bg-gradient-to-br from-quantum-950/60 via-slate-900/80 to-slate-950 border border-quantum-500/30 flex flex-col gap-3.5 shadow-lg">
                      {/* Header */}
                      <div className="flex items-center justify-between border-b border-quantum-500/20 pb-2">
                        <div className="flex items-center space-x-2">
                          <Atom className="w-4 h-4 text-quantum-400 animate-pulse" />
                          <span className="text-xs font-bold text-quantum-200 tracking-wide uppercase">
                            Quantum Decision & Media RAG Engine
                          </span>
                        </div>
                        <span className="text-[11px] font-mono font-bold text-quantum-300 px-2.5 py-0.5 rounded-full bg-quantum-500/20 border border-quantum-500/40">
                          {Math.round(latestAudio.quantum_metrics.quantum_fidelity * 100)}% Canonical Overlap
                        </span>
                      </div>

                      {/* Concrete Audio & Video Reference Box */}
                      {latestAudio.quantum_metrics.audio_video_reference && (
                        <div className="p-3 rounded-lg bg-slate-950/70 border border-cyan-500/20 flex flex-col gap-1.5">
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] uppercase font-bold text-cyan-400 flex items-center space-x-1">
                              <Film className="w-3 h-3 mr-1" />
                              Audio / Video Grounded Scene
                            </span>
                            {(latestAudio.quantum_metrics.audio_video_reference.clip_timestamp || latestAudio.quantum_metrics.audio_video_reference.scene_timestamp) && (
                              <span className="text-[10px] font-mono text-cyan-300/80 bg-cyan-950/60 px-1.5 py-0.5 rounded border border-cyan-500/30">
                                {latestAudio.quantum_metrics.audio_video_reference.clip_timestamp || latestAudio.quantum_metrics.audio_video_reference.scene_timestamp}
                              </span>
                            )}
                          </div>
                          <span className="text-xs font-semibold text-slate-100">
                            {latestAudio.quantum_metrics.audio_video_reference.media_title}
                          </span>
                          <p className="text-[11px] text-slate-300 leading-relaxed font-sans">
                            {latestAudio.quantum_metrics.audio_video_reference.scene_context}
                          </p>

                          {/* Ground Truth Acoustic Benchmark */}
                          {latestAudio.quantum_metrics.audio_video_reference.acoustic_benchmark && (
                            <div className="mt-1 pt-1.5 border-t border-white/5 grid grid-cols-3 gap-1.5 text-[10px] font-mono text-slate-400">
                              <div>
                                <span className="text-slate-500 block">Ref F0 Pitch</span>
                                <span className="text-cyan-300 font-bold">
                                  {latestAudio.quantum_metrics.audio_video_reference.acoustic_benchmark.f0_median_hz} Hz
                                </span>
                              </div>
                              <div>
                                <span className="text-slate-500 block">Ref Tempo</span>
                                <span className="text-cyan-300 font-bold">
                                  {latestAudio.quantum_metrics.audio_video_reference.acoustic_benchmark.tempo_wpm} WPM
                                </span>
                              </div>
                              <div>
                                <span className="text-slate-500 block">Vocal Grit</span>
                                <span className="text-cyan-300 font-bold">
                                  {Math.round((latestAudio.quantum_metrics.audio_video_reference.acoustic_benchmark.vocal_grit || 0) * 100)}%
                                </span>
                              </div>
                            </div>
                          )}
                        </div>
                      )}

                      {/* Quantum Decision Engine Details */}
                      {latestAudio.quantum_metrics.quantum_decision && (
                        <div className="p-3 rounded-lg bg-slate-950/80 border border-purple-500/20 flex flex-col gap-2">
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] uppercase font-bold text-purple-400 flex items-center space-x-1">
                              <Cpu className="w-3 h-3 mr-1" />
                              Quantum Decision Circuit (PQDC)
                            </span>
                            <span className="text-[10px] font-medium text-amber-300 bg-amber-950/60 px-2 py-0.5 rounded border border-amber-500/30">
                              {latestAudio.quantum_metrics.quantum_decision.decided_delivery_mode}
                            </span>
                          </div>

                          {/* Pauli-Z Expectation Values */}
                          <div className="grid grid-cols-4 gap-1.5 text-center text-[10px] font-mono">
                            <div className="p-1.5 rounded bg-slate-900 border border-white/5">
                              <span className="text-slate-500 block">⟨Z₀⟩ Pitch</span>
                              <span className="text-purple-300 font-bold">
                                {latestAudio.quantum_metrics.quantum_decision.pauli_z_expectations[0]?.toFixed(2)}
                              </span>
                            </div>
                            <div className="p-1.5 rounded bg-slate-900 border border-white/5">
                              <span className="text-slate-500 block">⟨Z₁⟩ Rate</span>
                              <span className="text-purple-300 font-bold">
                                {latestAudio.quantum_metrics.quantum_decision.pauli_z_expectations[1]?.toFixed(2)}
                              </span>
                            </div>
                            <div className="p-1.5 rounded bg-slate-900 border border-white/5">
                              <span className="text-slate-500 block">⟨Z₂⟩ Drive</span>
                              <span className="text-purple-300 font-bold">
                                {latestAudio.quantum_metrics.quantum_decision.pauli_z_expectations[2]?.toFixed(2)}
                              </span>
                            </div>
                            <div className="p-1.5 rounded bg-slate-900 border border-white/5">
                              <span className="text-slate-500 block">⟨Z₃⟩ Formant</span>
                              <span className="text-purple-300 font-bold">
                                {latestAudio.quantum_metrics.quantum_decision.pauli_z_expectations[3]?.toFixed(2)}
                              </span>
                            </div>
                          </div>

                          {/* Quantum Decided Resolution */}
                          <p className="text-[10px] text-slate-400 italic leading-snug">
                            {latestAudio.quantum_metrics.quantum_decision.decision_rationale}
                          </p>
                        </div>
                      )}

                      {/* Quantum Affect & DSP Badges */}
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <div className="p-2 rounded-lg bg-slate-900/80 border border-white/5 flex flex-col">
                          <span className="text-[10px] text-slate-400">Quantum Affect</span>
                          <span className="text-white font-semibold capitalize flex items-center space-x-1">
                            <span>{latestAudio.quantum_metrics.quantum_emotion}</span>
                            <span className="text-[10px] text-quantum-400 font-mono">
                              (S={latestAudio.quantum_metrics.entanglement_entropy.toFixed(2)})
                            </span>
                          </span>
                        </div>

                        <div className="p-2 rounded-lg bg-slate-900/80 border border-white/5 flex flex-col">
                          <span className="text-[10px] text-slate-400">Active DSP Filter</span>
                          <span className="text-amber-300 font-semibold font-mono text-[11px] truncate">
                            {latestAudio.quantum_metrics.applied_dsp_filter.replace(/_/g, ' ')}
                          </span>
                        </div>
                      </div>

                      {/* Dynamic Tuning details */}
                      {(latestAudio.quantum_metrics.effective_pitch || latestAudio.quantum_metrics.effective_rate) && (
                        <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 bg-slate-950/60 px-2.5 py-1.5 rounded-lg border border-white/5">
                          <span>Quantum Pitch: <strong className="text-purple-300">{latestAudio.quantum_metrics.effective_pitch}</strong></span>
                          <span>Quantum Rate: <strong className="text-purple-300">{latestAudio.quantum_metrics.effective_rate}</strong></span>
                        </div>
                      )}
                    </div>
                  )}

                  <div className="pt-2">
                    <AudioPlayer result={latestAudio} currentText={text} />
                  </div>
                </div>
              ) : (
                <div className="py-12 text-center flex flex-col items-center justify-center text-slate-400 gap-3">
                  <div className="w-14 h-14 rounded-full bg-slate-800/60 border border-white/5 flex items-center justify-center">
                    <Volume2 className="w-6 h-6 text-slate-500" />
                  </div>
                  <p className="text-sm font-medium text-slate-300">No audio synthesized yet.</p>
                  <p className="text-xs text-slate-500 max-w-xs">
                    Enter text on the left and click "Generate Speech" to synthesize natural voice audio.
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Educational Callout: Quantum Intelligence Integration */}
          <div className="glass-panel rounded-2xl p-6 border border-quantum-500/20 shadow-xl relative overflow-hidden bg-gradient-to-br from-slate-900/90 via-slate-900/60 to-quantum-950/30">
            <div className="flex items-center space-x-3 mb-3">
              <div className="w-8 h-8 rounded-lg bg-quantum-500/20 border border-quantum-500/40 flex items-center justify-center">
                <Atom className="w-4 h-4 text-quantum-400" />
              </div>
              <h3 className="font-bold text-white text-sm">Quantum Intelligence Layer</h3>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed mb-4">
              Explore how your speech text maps onto quantum Hilbert state spaces. Test Variational Quantum Classifiers (VQC), PennyLane emotion QNNs, and quantum kernel similarity beside your speech pipeline.
            </p>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <Link
                to="/quantum/emotion"
                className="p-2.5 rounded-lg bg-slate-900/80 hover:bg-quantum-900/40 border border-white/5 text-slate-200 hover:text-quantum-300 font-medium transition text-center"
              >
                Analyze Text Emotion →
              </Link>
              <Link
                to="/quantum/circuits"
                className="p-2.5 rounded-lg bg-slate-900/80 hover:bg-quantum-900/40 border border-white/5 text-slate-200 hover:text-quantum-300 font-medium transition text-center"
              >
                Circuit Sandbox →
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Custom Voice Injection Modal */}
      <AddVoiceModal
        isOpen={isVoiceModalOpen}
        onClose={() => setIsVoiceModalOpen(false)}
        onSuccess={() => {
          queryClient.invalidateQueries({ queryKey: ['voices'] });
        }}
        languages={languages}
      />
    </div>
  );
};
