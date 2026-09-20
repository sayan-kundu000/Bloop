import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { FileText, Play, Clock, Cpu, CheckCircle, BarChart } from 'lucide-react';
import { QuantumNav } from '../../components/quantum/QuantumNav';
import { ProbabilityChart } from '../../components/quantum/ProbabilityChart';
import { quantumApi } from '../../api/client';
import { QuantumTextResult } from '../../types';

export const QuantumTextPage: React.FC = () => {
  const [inputText, setInputText] = useState(
    'The algorithm synthesizes high-dimensional quantum states using parameterized rotation gates and entangling unitary operations.'
  );
  const [numQubits, setNumQubits] = useState(4);
  const [shots, setShots] = useState(1024);
  const [result, setResult] = useState<QuantumTextResult | null>(null);

  const mutation = useMutation({
    mutationFn: quantumApi.analyzeText,
    onSuccess: (data) => setResult(data),
  });

  const handleRun = () => {
    if (!inputText.trim()) return;
    mutation.mutate({ text: inputText, num_qubits: numQubits, shots });
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center space-x-3">
          <FileText className="w-8 h-8 text-quantum-400" />
          <span>Quantum <span className="gradient-text-quantum">Text Intelligence</span></span>
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Encodes lexical features into quantum states and classifies stylistic register via Variational Quantum Classifier.
        </p>
      </div>

      <QuantumNav />

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Experiment Controls (5 cols) */}
        <div className="lg:col-span-5 flex flex-col gap-6">
          <div className="glass-panel rounded-2xl p-6 border border-white/10 shadow-xl flex flex-col gap-4">
            <h3 className="font-bold text-white text-base border-b border-white/10 pb-3">
              Experiment Configuration
            </h3>

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                Input Text Prompt
              </label>
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                rows={4}
                className="w-full bg-slate-900/90 text-sm text-white rounded-xl p-3 border border-white/10 focus:outline-none focus:border-quantum-500"
                placeholder="Enter text to analyze..."
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                  Qubits ({numQubits})
                </label>
                <select
                  value={numQubits}
                  onChange={(e) => setNumQubits(parseInt(e.target.value))}
                  className="w-full bg-slate-900 text-sm text-white rounded-xl p-2.5 border border-white/10 focus:outline-none focus:border-quantum-500"
                >
                  <option value={2}>2 Qubits</option>
                  <option value={4}>4 Qubits</option>
                  <option value={6}>6 Qubits</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                  Measurement Shots
                </label>
                <select
                  value={shots}
                  onChange={(e) => setShots(parseInt(e.target.value))}
                  className="w-full bg-slate-900 text-sm text-white rounded-xl p-2.5 border border-white/10 focus:outline-none focus:border-quantum-500"
                >
                  <option value={512}>512 Shots</option>
                  <option value={1024}>1024 Shots</option>
                  <option value={2048}>2048 Shots</option>
                </select>
              </div>
            </div>

            <button
              onClick={handleRun}
              disabled={mutation.isPending || !inputText.trim()}
              className="mt-2 w-full py-3 rounded-xl bg-gradient-to-r from-quantum-600 to-bloop-600 hover:from-quantum-500 hover:to-bloop-500 text-white font-semibold text-sm shadow-lg shadow-quantum-600/30 flex items-center justify-center space-x-2 transition disabled:opacity-50"
            >
              {mutation.isPending ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Simulating Quantum Circuit...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-current" />
                  <span>Run Quantum Classification</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right Column: Classification & Simulation Results (7 cols) */}
        <div className="lg:col-span-7 flex flex-col gap-6">
          {result ? (
            <div className="glass-panel rounded-2xl p-6 border border-white/10 shadow-xl flex flex-col gap-5">
              <div className="flex items-center justify-between border-b border-white/10 pb-3">
                <span className="font-bold text-white text-base">Quantum VQC Results</span>
                <span className="text-xs text-slate-400 font-mono flex items-center space-x-1">
                  <Clock className="w-3.5 h-3.5" />
                  <span>{result.execution_time_ms} ms</span>
                </span>
              </div>

              {/* Comparative Outcome Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="p-4 rounded-xl bg-gradient-to-br from-quantum-950/60 to-slate-900/80 border border-quantum-500/30">
                  <span className="text-xs font-mono text-quantum-300 block mb-1">
                    Quantum VQC Classifier
                  </span>
                  <div className="text-xl font-black text-white capitalize">
                    {result.predicted_style}
                  </div>
                  <div className="text-xs text-slate-300 mt-2 flex items-center justify-between">
                    <span>Confidence Score</span>
                    <span className="font-bold text-quantum-300">
                      {Math.round(result.confidence * 100)}%
                    </span>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-slate-900/70 border border-white/10">
                  <span className="text-xs font-mono text-slate-400 block mb-1">
                    Classical Baseline
                  </span>
                  <div className="text-xl font-bold text-slate-200 capitalize">
                    {result.classical_baseline_prediction}
                  </div>
                  <div className="text-xs text-slate-400 mt-2 flex items-center justify-between">
                    <span>Confidence Score</span>
                    <span className="font-medium text-slate-300">
                      {Math.round(result.classical_confidence * 100)}%
                    </span>
                  </div>
                </div>
              </div>

              {/* Quantum State Probabilities */}
              <ProbabilityChart
                probabilities={result.quantum_probabilities}
                title="Measurement State Probabilities (Aer Simulator)"
              />

              {/* Metadata row */}
              <div className="grid grid-cols-3 gap-2 text-xs font-mono text-slate-400 text-center pt-2 border-t border-white/5">
                <div className="p-2 rounded bg-slate-900/50">
                  <span className="text-[10px] block text-slate-500">Qubits</span>
                  <span className="text-white font-bold">{result.num_qubits}</span>
                </div>
                <div className="p-2 rounded bg-slate-900/50">
                  <span className="text-[10px] block text-slate-500">Circuit Depth</span>
                  <span className="text-white font-bold">{result.circuit_depth}</span>
                </div>
                <div className="p-2 rounded bg-slate-900/50">
                  <span className="text-[10px] block text-slate-500">Feature Angles</span>
                  <span className="text-white font-bold">{result.classical_features.length}</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="glass-panel rounded-2xl p-12 text-center border border-white/10 text-slate-400 flex flex-col items-center justify-center gap-3">
              <BarChart className="w-10 h-10 text-slate-600" />
              <p className="text-base font-semibold text-white">No active simulation run</p>
              <p className="text-xs text-slate-500 max-w-sm">
                Click "Run Quantum Classification" to encode your text into quantum states and execute the Qiskit simulator.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
