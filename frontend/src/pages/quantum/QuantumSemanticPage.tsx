import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { GitCompare, Play, Clock, Sparkles, AlertCircle, Layers, Cpu, ShieldCheck, Activity } from 'lucide-react';
import { QuantumNav } from '../../components/quantum/QuantumNav';
import { quantumApi } from '../../api/client';
import { QuantumSemanticResult } from '../../types';

export const QuantumSemanticPage: React.FC = () => {
  const [textA, setTextA] = useState(
    'Artificial intelligence converts text into natural sounding voice audio.'
  );
  const [textB, setTextB] = useState(
    'AI models synthesize speech output from written language input.'
  );
  const [method, setMethod] = useState<'hybrid' | 'classical' | 'quantum'>('hybrid');
  const [framework, setFramework] = useState<'qiskit' | 'pennylane'>('qiskit');
  const [numQubits, setNumQubits] = useState(4);
  const [shots, setShots] = useState(1024);
  const [result, setResult] = useState<QuantumSemanticResult | null>(null);

  const mutation = useMutation({
    mutationFn: quantumApi.analyzeSemantics,
    onSuccess: (data) => setResult(data),
  });

  const handleRun = () => {
    if (!textA.trim() || !textB.trim()) return;
    mutation.mutate({
      text_a: textA,
      text_b: textB,
      method,
      framework,
      num_qubits: numQubits,
      shots,
    });
  };

  const loadSamplePair = (type: 'identical' | 'paraphrase' | 'topical' | 'unrelated') => {
    if (type === 'identical') {
      setTextA('Quantum computing utilizes superposition and entanglement to process information.');
      setTextB('Quantum computing utilizes superposition and entanglement to process information.');
    } else if (type === 'paraphrase') {
      setTextA('The speech engine synthesizes natural vocal audio from text inputs.');
      setTextB('Text input is converted into natural sounding voice audio by the synthesis engine.');
    } else if (type === 'topical') {
      setTextA('Text to speech systems modulate acoustic pitch, cadence, and vocal tempo.');
      setTextB('Digital audio workstations record multichannel music and vocal performances.');
    } else {
      setTextA('Quantum statevector fidelity measures state transition overlap in Hilbert space.');
      setTextB('The quick brown fox jumps over the lazy sleeping dog in the park.');
    }
  };

  const getVerdictBadge = (verdict: string) => {
    if (verdict.includes('Identical') || verdict.includes('Strongly')) {
      return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30';
    } else if (verdict.includes('Moderately')) {
      return 'bg-amber-500/20 text-amber-300 border-amber-500/30';
    }
    return 'bg-rose-500/20 text-rose-300 border-rose-500/30';
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center space-x-3">
          <GitCompare className="w-8 h-8 text-teal-400" />
          <span>Quantum <span className="gradient-text-quantum">Semantic Similarity</span></span>
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Estimates semantic similarity via classical TF-IDF baseline, TruncatedSVD reduction, and Quantum Kernel Transition State Overlap |⟨φ(A)|ψ(B)⟩|².
        </p>
      </div>

      <QuantumNav />

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Input Prompts & Controls (5 cols) */}
        <div className="lg:col-span-5 flex flex-col gap-5">
          <div className="glass-panel rounded-2xl p-6 border border-white/10 shadow-xl flex flex-col gap-4">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <h3 className="font-bold text-white text-base">
                Prompts for Comparison
              </h3>
              <span className="text-xs text-slate-400">Research Sandbox</span>
            </div>

            {/* Quick Sample Selector */}
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                Load Benchmark Presets
              </label>
              <div className="grid grid-cols-4 gap-1.5">
                <button
                  type="button"
                  onClick={() => loadSamplePair('identical')}
                  className="px-2 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 transition"
                >
                  Identical
                </button>
                <button
                  type="button"
                  onClick={() => loadSamplePair('paraphrase')}
                  className="px-2 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 transition"
                >
                  Paraphrase
                </button>
                <button
                  type="button"
                  onClick={() => loadSamplePair('topical')}
                  className="px-2 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 transition"
                >
                  Topical
                </button>
                <button
                  type="button"
                  onClick={() => loadSamplePair('unrelated')}
                  className="px-2 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 transition"
                >
                  Unrelated
                </button>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                Text Prompt A
              </label>
              <textarea
                value={textA}
                onChange={(e) => setTextA(e.target.value)}
                rows={3}
                className="w-full bg-slate-900/90 text-sm text-white rounded-xl p-3 border border-white/10 focus:outline-none focus:border-teal-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                Text Prompt B
              </label>
              <textarea
                value={textB}
                onChange={(e) => setTextB(e.target.value)}
                rows={3}
                className="w-full bg-slate-900/90 text-sm text-white rounded-xl p-3 border border-white/10 focus:outline-none focus:border-teal-500"
              />
            </div>

            {/* Analysis Method & Framework */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Analysis Method
                </label>
                <select
                  value={method}
                  onChange={(e) => setMethod(e.target.value as any)}
                  className="w-full bg-slate-900 text-sm text-white rounded-xl p-2.5 border border-white/10 focus:outline-none focus:border-teal-500"
                >
                  <option value="hybrid">Hybrid (Quantum + Classical)</option>
                  <option value="classical">Classical Baseline Only</option>
                  <option value="quantum">Quantum Kernel Only</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Simulator Framework
                </label>
                <select
                  value={framework}
                  onChange={(e) => setFramework(e.target.value as any)}
                  className="w-full bg-slate-900 text-sm text-white rounded-xl p-2.5 border border-white/10 focus:outline-none focus:border-teal-500"
                >
                  <option value="qiskit">Qiskit Aer Simulator</option>
                  <option value="pennylane">PennyLane default.qubit</option>
                </select>
              </div>
            </div>

            {/* Qubits & Shots */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Hilbert Register ({numQubits} Qubits)
                </label>
                <select
                  value={numQubits}
                  onChange={(e) => setNumQubits(parseInt(e.target.value))}
                  className="w-full bg-slate-900 text-sm text-white rounded-xl p-2.5 border border-white/10 focus:outline-none focus:border-teal-500"
                >
                  <option value={2}>2 Qubits (4 Dimensions)</option>
                  <option value={4}>4 Qubits (16 Dimensions)</option>
                  <option value={6}>6 Qubits (64 Dimensions)</option>
                  <option value={8}>8 Qubits (256 Dimensions)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Shots
                </label>
                <select
                  value={shots}
                  onChange={(e) => setShots(parseInt(e.target.value))}
                  className="w-full bg-slate-900 text-sm text-white rounded-xl p-2.5 border border-white/10 focus:outline-none focus:border-teal-500"
                >
                  <option value={512}>512 Shots</option>
                  <option value={1024}>1024 Shots</option>
                  <option value={2048}>2048 Shots</option>
                </select>
              </div>
            </div>

            <button
              onClick={handleRun}
              disabled={mutation.isPending || !textA.trim() || !textB.trim()}
              className="mt-2 w-full py-3.5 rounded-xl bg-gradient-to-r from-teal-600 via-bloop-600 to-quantum-600 hover:opacity-95 text-white font-semibold text-sm shadow-lg shadow-teal-600/20 flex items-center justify-center space-x-2 transition disabled:opacity-50"
            >
              {mutation.isPending ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Computing Semantic Overlap...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-current" />
                  <span>Run Semantic Similarity Analysis</span>
                </>
              )}
            </button>

            {mutation.isError && (
              <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-start space-x-2 text-rose-300 text-xs">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                <span>{(mutation.error as any)?.message || 'Semantic analysis request failed.'}</span>
              </div>
            )}
          </div>
        </div>

        {/* Results (7 cols) */}
        <div className="lg:col-span-7 flex flex-col gap-6">
          {result ? (
            <div className="glass-panel rounded-2xl p-6 border border-white/10 shadow-xl flex flex-col gap-5">
              <div className="flex items-center justify-between border-b border-white/10 pb-3">
                <div className="flex items-center space-x-2">
                  <span className="font-bold text-white text-base">Semantic Overlap Analysis</span>
                  <span className="text-xs px-2 py-0.5 rounded-md bg-teal-500/10 text-teal-300 border border-teal-500/20 uppercase font-mono">
                    {result.method || 'Hybrid'}
                  </span>
                </div>
                <span className="text-xs text-slate-400 font-mono flex items-center space-x-1">
                  <Clock className="w-3.5 h-3.5" />
                  <span>{result.execution_time_ms} ms</span>
                </span>
              </div>

              {/* Verdict Banner */}
              <div className="p-4 rounded-xl bg-slate-900/80 border border-white/10 flex items-center justify-between">
                <div>
                  <span className="text-xs text-slate-400 block mb-0.5">Similarity Verdict</span>
                  <span className="text-lg font-bold text-white">{result.similarity_verdict}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`text-xs px-3 py-1 rounded-full font-semibold border ${getVerdictBadge(result.similarity_verdict)}`}>
                    {Math.round((result.similarity_score ?? result.quantum_kernel_similarity) * 100)}% Match
                  </span>
                </div>
              </div>

              {/* Dual Metric Comparison Gauges */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="p-4 rounded-xl bg-gradient-to-br from-teal-950/60 to-slate-900/80 border border-teal-500/30">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-mono text-teal-300">
                      Quantum Kernel Fidelity |⟨φ|ψ⟩|²
                    </span>
                    <Cpu className="w-3.5 h-3.5 text-teal-400" />
                  </div>
                  <div className="text-3xl font-black text-white font-mono">
                    {result.quantum_kernel_similarity}
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-2 mt-3 overflow-hidden">
                    <div
                      className="h-full bg-teal-400 transition-all duration-500"
                      style={{ width: `${Math.round(result.quantum_kernel_similarity * 100)}%` }}
                    />
                  </div>
                  <span className="text-[10px] text-slate-400 mt-2 block">
                    {result.num_qubits} Qubits • Depth {result.circuit_depth} • {result.quantum_framework || 'qiskit'}
                  </span>
                </div>

                <div className="p-4 rounded-xl bg-slate-900/70 border border-white/10">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-mono text-slate-400">
                      Classical Cosine Baseline
                    </span>
                    <ShieldCheck className="w-3.5 h-3.5 text-slate-400" />
                  </div>
                  <div className="text-3xl font-black text-slate-200 font-mono">
                    {result.classical_cosine_similarity}
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-2 mt-3 overflow-hidden">
                    <div
                      className="h-full bg-slate-400 transition-all duration-500"
                      style={{ width: `${Math.round(result.classical_cosine_similarity * 100)}%` }}
                    />
                  </div>
                  <span className="text-[10px] text-slate-400 mt-2 block">
                    TF-IDF Representation • Normalized Vector Dot Product
                  </span>
                </div>
              </div>

              {/* Research Metrics: Divergence and Semantic Distance */}
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-xl bg-slate-950/60 border border-white/5 text-xs text-slate-400 flex items-center justify-between">
                  <span>Divergence |Q - C|:</span>
                  <span className="font-mono text-white font-bold">{result.divergence}</span>
                </div>

                <div className="p-3 rounded-xl bg-slate-950/60 border border-white/5 text-xs text-slate-400 flex items-center justify-between">
                  <span>Semantic Distance (1 - sim):</span>
                  <span className="font-mono text-white font-bold">
                    {result.semantic_distance ?? (1.0 - result.quantum_kernel_similarity).toFixed(4)}
                  </span>
                </div>
              </div>

              {/* Representation Details */}
              <div className="p-4 rounded-xl bg-slate-900/60 border border-white/10 text-xs space-y-2">
                <div className="flex items-center space-x-2 font-semibold text-white">
                  <Layers className="w-4 h-4 text-teal-400" />
                  <span>Pipeline Architecture & Representation</span>
                </div>
                <div className="grid grid-cols-2 gap-y-1 text-slate-400 pt-1">
                  <span>Representation Method:</span>
                  <span className="text-slate-200 font-mono">{result.representation_method || 'TF-IDF (Sublinear)'}</span>
                  <span>Feature Dimension:</span>
                  <span className="text-slate-200 font-mono">{result.feature_dimension || 64} features</span>
                  <span>Reduction Technique:</span>
                  <span className="text-slate-200 font-mono">{result.reduction_method || 'TruncatedSVD / Pooling'}</span>
                  <span>Quantum Encoding:</span>
                  <span className="text-slate-200 font-mono">{result.encoding_method || 'Ry Continuous Angles'}</span>
                </div>
              </div>

              {/* Pipeline Steps */}
              {result.pipeline_steps && result.pipeline_steps.length > 0 && (
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {result.pipeline_steps.map((step, idx) => (
                    <span
                      key={idx}
                      className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-white/5 font-mono"
                    >
                      {step}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="glass-panel rounded-2xl p-12 text-center border border-white/10 text-slate-400 flex flex-col items-center justify-center gap-3">
              <GitCompare className="w-10 h-10 text-slate-600" />
              <p className="text-base font-semibold text-white">No comparison executed yet</p>
              <p className="text-xs text-slate-500 max-w-sm">
                Enter two text prompts or click one of the presets above, then click "Run Semantic Similarity Analysis".
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
