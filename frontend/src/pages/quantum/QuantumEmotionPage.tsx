import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Heart, Play, Clock, Sparkles, Activity, Layers } from 'lucide-react';
import { QuantumNav } from '../../components/quantum/QuantumNav';
import { ProbabilityChart } from '../../components/quantum/ProbabilityChart';
import { quantumApi } from '../../api/client';
import { QuantumEmotionResult } from '../../types';

export const QuantumEmotionPage: React.FC = () => {
  const [text, setText] = useState(
    'I am deeply thrilled and delighted by the magnificent warmth of this natural synthetic voice!'
  );
  const [shots, setShots] = useState(1024);
  const [result, setResult] = useState<QuantumEmotionResult | null>(null);

  const mutation = useMutation({
    mutationFn: quantumApi.analyzeEmotion,
    onSuccess: (data) => setResult(data),
  });

  const handleRun = () => {
    if (!text.trim()) return;
    mutation.mutate({ text, shots });
  };

  const getEmotionColor = (emo: string) => {
    switch (emo) {
      case 'joy':
        return 'text-amber-400 bg-amber-400/10 border-amber-400/30';
      case 'sadness':
        return 'text-blue-400 bg-blue-400/10 border-blue-400/30';
      case 'anger':
        return 'text-rose-400 bg-rose-400/10 border-rose-400/30';
      default:
        return 'text-slate-300 bg-slate-800 border-white/10';
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center space-x-3">
          <Heart className="w-8 h-8 text-rose-400" />
          <span>Quantum <span className="gradient-text-quantum">Emotion Intelligence</span></span>
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Analyzes affective dimensions and sentiment using PennyLane Hybrid Quantum Neural Networks and entanglement metrics.
        </p>
      </div>

      <QuantumNav />

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Input (5 cols) */}
        <div className="lg:col-span-5 flex flex-col gap-6">
          <div className="glass-panel rounded-2xl p-6 border border-white/10 shadow-xl flex flex-col gap-4">
            <h3 className="font-bold text-white text-base border-b border-white/10 pb-3">
              Emotional Text Input
            </h3>

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                Speech Text to Analyze
              </label>
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                rows={5}
                className="w-full bg-slate-900/90 text-sm text-white rounded-xl p-3 border border-white/10 focus:outline-none focus:border-quantum-500"
                placeholder="Enter text to analyze sentiment & emotion..."
              />
            </div>

            <div className="flex flex-wrap gap-2 text-xs">
              <span className="text-slate-400 self-center">Try:</span>
              <button
                type="button"
                onClick={() =>
                  setText('I am extremely joyful and happy about this remarkable breakthrough!')
                }
                className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300"
              >
                Joy Sample
              </button>
              <button
                type="button"
                onClick={() =>
                  setText('A profound sorrow and grief enveloped the quiet empty room.')
                }
                className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300"
              >
                Sadness Sample
              </button>
              <button
                type="button"
                onClick={() =>
                  setText('I am outraged and furious by this inexcusable and hostile behavior!')
                }
                className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300"
              >
                Anger Sample
              </button>
            </div>

            <button
              onClick={handleRun}
              disabled={mutation.isPending || !text.trim()}
              className="mt-3 w-full py-3.5 rounded-xl bg-gradient-to-r from-rose-600 via-quantum-600 to-bloop-600 hover:opacity-95 text-white font-semibold text-sm shadow-lg shadow-rose-600/20 flex items-center justify-center space-x-2 transition disabled:opacity-50"
            >
              {mutation.isPending ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Evaluating PennyLane QNN...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-current" />
                  <span>Execute Emotion QNN</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right Column: QNN Analysis & Entanglement (7 cols) */}
        <div className="lg:col-span-7 flex flex-col gap-6">
          {result ? (
            <div className="glass-panel rounded-2xl p-6 border border-white/10 shadow-xl flex flex-col gap-5">
              <div className="flex items-center justify-between border-b border-white/10 pb-3">
                <span className="font-bold text-white text-base">PennyLane QNN Results</span>
                <span className="text-xs text-slate-400 font-mono flex items-center space-x-1">
                  <Clock className="w-3.5 h-3.5" />
                  <span>{result.execution_time_ms} ms</span>
                </span>
              </div>

              {/* Detected Emotion Card */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className={`p-4 rounded-xl border ${getEmotionColor(result.detected_emotion)}`}>
                  <span className="text-xs font-mono block mb-1 opacity-80">
                    PennyLane Hybrid QNN
                  </span>
                  <div className="text-2xl font-black capitalize flex items-center space-x-2">
                    <span>{result.detected_emotion}</span>
                    <Sparkles className="w-5 h-5" />
                  </div>
                  <div className="text-xs mt-2 flex items-center justify-between opacity-90">
                    <span>Confidence</span>
                    <span className="font-bold">{Math.round(result.hybrid_qnn_confidence * 100)}%</span>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-slate-900/70 border border-white/10">
                  <span className="text-xs font-mono text-slate-400 block mb-1">
                    Entanglement Entropy
                  </span>
                  <div className="text-2xl font-black text-quantum-300 font-mono">
                    {result.entanglement_entropy}
                  </div>
                  <p className="text-[11px] text-slate-500 mt-2">
                    Shannon entropy H = -Σ p log₂(p) over the 4-qubit affective state
                  </p>
                </div>
              </div>

              {/* Multi-class probability distribution */}
              <ProbabilityChart
                probabilities={result.quantum_probabilities}
                title="Affective Valence State Probabilities"
              />

              <div className="p-3.5 rounded-xl bg-slate-950/60 border border-white/5 text-xs text-slate-400 flex items-center justify-between">
                <span>Classical Lexical Baseline:</span>
                <span className="font-semibold text-white capitalize">
                  {result.classical_baseline_emotion} ({Math.round(result.classical_confidence * 100)}%)
                </span>
              </div>
            </div>
          ) : (
            <div className="glass-panel rounded-2xl p-12 text-center border border-white/10 text-slate-400 flex flex-col items-center justify-center gap-3">
              <Activity className="w-10 h-10 text-slate-600" />
              <p className="text-base font-semibold text-white">No active emotion analysis</p>
              <p className="text-xs text-slate-500 max-w-sm">
                Click "Execute Emotion QNN" to simulate the 4-qubit entangled affective classifier.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
