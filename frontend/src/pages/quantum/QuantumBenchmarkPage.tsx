import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  BarChart2,
  Play,
  CheckCircle2,
  TrendingUp,
  Clock,
  Info,
  Sliders,
  Cpu,
  Layers,
  Volume2,
  ArrowRight,
  Sparkles,
  Database,
  Activity,
} from 'lucide-react';
import { QuantumNav } from '../../components/quantum/QuantumNav';
import { quantumApi } from '../../api/client';
import { QuantumBenchmarkResult, SpeechRecommendation } from '../../types';

export const QuantumBenchmarkPage: React.FC = () => {
  const navigate = useNavigate();

  // Benchmark Category Selection
  const [category, setCategory] = useState<string>('text_classification');

  // Parameters
  const [datasetSize, setDatasetSize] = useState<number>(40);
  const [numQubits, setNumQubits] = useState<number>(4);
  const [shots, setShots] = useState<number>(512);
  const [classicalWeight, setClassicalWeight] = useState<number>(0.5);
  const [randomSeed, setRandomSeed] = useState<number>(42);

  // Result & Applied State
  const [result, setResult] = useState<QuantumBenchmarkResult | null>(null);
  const [appliedFeedback, setAppliedFeedback] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: quantumApi.runBenchmark,
    onSuccess: (data) => {
      setResult(data);
      setAppliedFeedback(null);
    },
  });

  const handleRun = () => {
    mutation.mutate({
      category,
      dataset_size: datasetSize,
      num_qubits: numQubits,
      shots,
      test_split: 0.25,
      random_seed: randomSeed,
      classical_weight: classicalWeight,
      quantum_weight: parseFloat((1.0 - classicalWeight).toFixed(2)),
    });
  };

  const handleApplyToTTS = (rec: SpeechRecommendation) => {
    // Store preset in localStorage for the TTS studio page
    const preset = {
      speed: rec.speed,
      pitch: rec.pitch,
      emotion: rec.style.charAt(0).toUpperCase() + rec.style.slice(1),
      settings: {
        stability: rec.stability,
        similarity_boost: rec.similarity_boost,
        style: rec.style === 'expressive' ? 0.2 : 0.0,
      },
      source: 'Quantum Hybrid Intelligence',
    };
    localStorage.setItem('bloop_tts_preset', JSON.stringify(preset));
    setAppliedFeedback(`Applied recommended acoustic parameters (Speed: ${rec.speed}x, Pitch: ${rec.pitch}x, Stability: ${rec.stability}). Redirecting to Speech Studio...`);
    setTimeout(() => {
      navigate('/app/generate');
    }, 1200);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Page Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center space-x-3">
          <BarChart2 className="w-8 h-8 text-amber-400" />
          <span>Quantum vs Classical <span className="gradient-text-quantum">Benchmarking & Hybrid Intelligence</span></span>
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Honest empirical evaluation across classical baselines, quantum circuits, and hybrid fusion pipelines.
        </p>
      </div>

      <QuantumNav />

      {/* Category Selection Tabs */}
      <div className="flex flex-wrap gap-2 mb-8 p-1.5 glass-panel rounded-2xl border border-white/10">
        {[
          { id: 'text_classification', label: 'Type A: Text Classifier', icon: Cpu },
          { id: 'emotion_qnn', label: 'Type B: Emotion QNN', icon: Sparkles },
          { id: 'semantic_similarity', label: 'Type C: Semantic Kernel', icon: Layers },
          { id: 'circuit_noise', label: 'Type D: Circuit Simulation', icon: Activity },
          { id: 'hybrid_speech_pipeline', label: 'Type E: Hybrid Speech Pipeline', icon: Volume2 },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = category === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => {
                setCategory(tab.id);
                setResult(null);
                setAppliedFeedback(null);
              }}
              className={`flex items-center space-x-2 px-4 py-2.5 rounded-xl text-xs font-semibold transition-all duration-200 ${
                isActive
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30 shadow-lg shadow-amber-500/10'
                  : 'text-slate-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-amber-400' : 'text-slate-500'}`} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Controls Column (4 cols) */}
        <div className="lg:col-span-4 flex flex-col gap-6">
          <div className="glass-panel rounded-2xl p-6 border border-white/10 shadow-xl flex flex-col gap-4">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <h3 className="font-bold text-white text-base flex items-center space-x-2">
                <Sliders className="w-4 h-4 text-amber-400" />
                <span>Benchmark Controls</span>
              </h3>
              <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-amber-300 font-mono">
                {category.toUpperCase().replace('_', ' ')}
              </span>
            </div>

            {/* Dataset Size Slider */}
            {category !== 'circuit_noise' && category !== 'hybrid_speech_pipeline' && (
              <div>
                <div className="flex justify-between items-center text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  <span>Dataset Samples</span>
                  <span className="font-mono text-amber-400">{datasetSize}</span>
                </div>
                <input
                  type="range"
                  min="20"
                  max="100"
                  step="10"
                  value={datasetSize}
                  onChange={(e) => setDatasetSize(parseInt(e.target.value))}
                  className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-500 mt-2"
                />
              </div>
            )}

            {/* Qubit Count Selector */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                Quantum Feature Register
              </label>
              <select
                value={numQubits}
                onChange={(e) => setNumQubits(parseInt(e.target.value))}
                className="w-full bg-slate-900 text-sm text-white rounded-xl p-2.5 border border-white/10 focus:outline-none focus:border-amber-500"
              >
                <option value={2}>2 Qubits (Angle Encoded)</option>
                <option value={4}>4 Qubits (Entangled Ansatz)</option>
                <option value={6}>6 Qubits (Hilbert Space: 64 Dim)</option>
              </select>
            </div>

            {/* Shots Selector */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                Simulator Measurement Shots
              </label>
              <select
                value={shots}
                onChange={(e) => setShots(parseInt(e.target.value))}
                className="w-full bg-slate-900 text-sm text-white rounded-xl p-2.5 border border-white/10 focus:outline-none focus:border-amber-500"
              >
                <option value={256}>256 Shots (Fast Simulation)</option>
                <option value={512}>512 Shots (Balanced)</option>
                <option value={1024}>1024 Shots (High Statistical Precision)</option>
              </select>
            </div>

            {/* Fusion Weight Slider */}
            {(category === 'semantic_similarity' || category === 'hybrid_speech_pipeline') && (
              <div>
                <div className="flex justify-between items-center text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  <span>Classical vs Quantum Weight</span>
                  <span className="font-mono text-amber-400">
                    α={classicalWeight.toFixed(2)} / β={(1 - classicalWeight).toFixed(2)}
                  </span>
                </div>
                <input
                  type="range"
                  min="0.0"
                  max="1.0"
                  step="0.1"
                  value={classicalWeight}
                  onChange={(e) => setClassicalWeight(parseFloat(e.target.value))}
                  className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-500 mt-2"
                />
                <div className="flex justify-between text-[10px] text-slate-500 mt-1">
                  <span>100% Classical</span>
                  <span>50/50 Fusion</span>
                  <span>100% Quantum</span>
                </div>
              </div>
            )}

            {/* Deterministic Seed */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                Reproducibility Seed
              </label>
              <input
                type="number"
                value={randomSeed}
                onChange={(e) => setRandomSeed(parseInt(e.target.value) || 42)}
                className="w-full bg-slate-900 text-sm text-white rounded-xl p-2.5 border border-white/10 focus:outline-none focus:border-amber-500 font-mono"
              />
            </div>

            {/* Run Button */}
            <button
              onClick={handleRun}
              disabled={mutation.isPending}
              className="mt-3 w-full py-3.5 rounded-xl bg-gradient-to-r from-amber-600 via-orange-600 to-bloop-600 hover:opacity-95 text-white font-semibold text-sm shadow-lg shadow-amber-600/20 flex items-center justify-center space-x-2 transition"
            >
              {mutation.isPending ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Evaluating Candidate Models...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-current" />
                  <span>Execute {category.replace('_', ' ').toUpperCase()} Benchmark</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Results & Analysis Column (8 cols) */}
        <div className="lg:col-span-8 flex flex-col gap-6">
          {appliedFeedback && (
            <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center space-x-3 text-emerald-300 text-sm">
              <CheckCircle2 className="w-5 h-5 shrink-0 text-emerald-400" />
              <span>{appliedFeedback}</span>
            </div>
          )}

          {result ? (
            <div className="glass-panel rounded-2xl p-6 border border-white/10 shadow-xl flex flex-col gap-6">
              {/* Header & Dataset Audit Badge */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-white/10 pb-4 gap-2">
                <div>
                  <h2 className="font-bold text-white text-lg flex items-center space-x-2">
                    <TrendingUp className="w-5 h-5 text-amber-400" />
                    <span>Benchmark Evaluation Results</span>
                  </h2>
                  <p className="text-xs text-slate-400 font-mono mt-0.5">{result.summary}</p>
                </div>
                {result.dataset && (
                  <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-slate-900 border border-white/10 text-xs text-slate-300">
                    <Database className="w-3.5 h-3.5 text-amber-400" />
                    <span className="font-medium">{result.dataset.dataset_name}</span>
                    <span className="text-slate-500">({result.dataset.sample_count} samples)</span>
                  </div>
                )}
              </div>

              {/* Comparative Metrics Table */}
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-white/10 text-slate-400">
                      <th className="py-2.5 px-3">Evaluation Metric</th>
                      <th className="py-2.5 px-3 text-bloop-300 font-semibold">{result.classical_model}</th>
                      <th className="py-2.5 px-3 text-quantum-300 font-semibold">{result.quantum_model}</th>
                      {result.hybrid_model && (
                        <th className="py-2.5 px-3 text-amber-300 font-semibold">{result.hybrid_model}</th>
                      )}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5 font-mono text-slate-200">
                    {/* Accuracy */}
                    {result.classical_metrics.accuracy !== undefined && result.classical_metrics.accuracy !== null && (
                      <tr>
                        <td className="py-2.5 px-3 font-sans text-slate-300">Accuracy</td>
                        <td className="py-2.5 px-3 font-bold">{Math.round((result.classical_metrics.accuracy ?? 0) * 100)}%</td>
                        <td className="py-2.5 px-3 font-bold text-quantum-300">{result.quantum_metrics.accuracy != null ? `${Math.round(result.quantum_metrics.accuracy * 100)}%` : '-'}</td>
                        {result.hybrid_metrics && (
                          <td className="py-2.5 px-3 font-bold text-amber-300">{result.hybrid_metrics.accuracy != null ? `${Math.round(result.hybrid_metrics.accuracy * 100)}%` : '-'}</td>
                        )}
                      </tr>
                    )}

                    {/* Precision & Recall */}
                    {result.classical_metrics.precision !== undefined && result.classical_metrics.precision !== null && (
                      <>
                        <tr>
                          <td className="py-2.5 px-3 font-sans text-slate-300">Precision</td>
                          <td className="py-2.5 px-3">{result.classical_metrics.precision}</td>
                          <td className="py-2.5 px-3 text-quantum-300">{result.quantum_metrics.precision}</td>
                          {result.hybrid_metrics && <td className="py-2.5 px-3 text-amber-300">{result.hybrid_metrics.precision ?? '-'}</td>}
                        </tr>
                        <tr>
                          <td className="py-2.5 px-3 font-sans text-slate-300">Recall</td>
                          <td className="py-2.5 px-3">{result.classical_metrics.recall}</td>
                          <td className="py-2.5 px-3 text-quantum-300">{result.quantum_metrics.recall}</td>
                          {result.hybrid_metrics && <td className="py-2.5 px-3 text-amber-300">{result.hybrid_metrics.recall ?? '-'}</td>}
                        </tr>
                      </>
                    )}

                    {/* F1 Score */}
                    {result.classical_metrics.f1_score !== undefined && result.classical_metrics.f1_score !== null && (
                      <tr>
                        <td className="py-2.5 px-3 font-sans text-slate-300 font-semibold">F1-Score</td>
                        <td className="py-2.5 px-3 font-bold text-emerald-400">{result.classical_metrics.f1_score}</td>
                        <td className="py-2.5 px-3 font-bold text-quantum-300">{result.quantum_metrics.f1_score}</td>
                        {result.hybrid_metrics && <td className="py-2.5 px-3 font-bold text-amber-300">{result.hybrid_metrics.f1_score ?? '-'}</td>}
                      </tr>
                    )}

                    {/* MAE & Correlation (for Semantic Benchmarks) */}
                    {result.classical_metrics.mae !== undefined && result.classical_metrics.mae !== null && (
                      <>
                        <tr>
                          <td className="py-2.5 px-3 font-sans text-slate-300">Mean Absolute Error (MAE)</td>
                          <td className="py-2.5 px-3 text-emerald-400 font-bold">{result.classical_metrics.mae}</td>
                          <td className="py-2.5 px-3 text-quantum-300 font-bold">{result.quantum_metrics.mae}</td>
                          {result.hybrid_metrics && <td className="py-2.5 px-3 text-amber-300 font-bold">{result.hybrid_metrics.mae}</td>}
                        </tr>
                        <tr>
                          <td className="py-2.5 px-3 font-sans text-slate-300">Pearson Correlation (r)</td>
                          <td className="py-2.5 px-3">{result.classical_metrics.correlation}</td>
                          <td className="py-2.5 px-3 text-quantum-300">{result.quantum_metrics.correlation}</td>
                          {result.hybrid_metrics && <td className="py-2.5 px-3 text-amber-300">{result.hybrid_metrics.correlation}</td>}
                        </tr>
                      </>
                    )}

                    {/* TVD and Fidelity (for Circuit Benchmarks) */}
                    {result.quantum_metrics.tvd !== undefined && result.quantum_metrics.tvd !== null && (
                      <>
                        <tr>
                          <td className="py-2.5 px-3 font-sans text-slate-300">Total Variation Distance (TVD)</td>
                          <td className="py-2.5 px-3">0.0000</td>
                          <td className="py-2.5 px-3 text-amber-400 font-bold">{result.quantum_metrics.tvd}</td>
                          {result.hybrid_metrics && <td className="py-2.5 px-3">-</td>}
                        </tr>
                        <tr>
                          <td className="py-2.5 px-3 font-sans text-slate-300">Classical Fidelity</td>
                          <td className="py-2.5 px-3 font-bold text-emerald-400">1.0000</td>
                          <td className="py-2.5 px-3 text-quantum-300 font-bold">{result.quantum_metrics.fidelity}</td>
                          {result.hybrid_metrics && <td className="py-2.5 px-3">-</td>}
                        </tr>
                      </>
                    )}

                    {/* Training Latency */}
                    {result.classical_metrics.training_time_seconds ? (
                      <tr>
                        <td className="py-2.5 px-3 font-sans text-slate-300">Training Time</td>
                        <td className="py-2.5 px-3 text-slate-400">{result.classical_metrics.training_time_seconds}s</td>
                        <td className="py-2.5 px-3 text-slate-400">{result.quantum_metrics.training_time_seconds}s</td>
                        {result.hybrid_metrics && <td className="py-2.5 px-3 text-slate-400">-</td>}
                      </tr>
                    ) : null}

                    {/* Inference Latency */}
                    <tr>
                      <td className="py-2.5 px-3 font-sans text-slate-300">Inference Latency</td>
                      <td className="py-2.5 px-3 text-emerald-400">{result.classical_metrics.inference_time_seconds}s</td>
                      <td className="py-2.5 px-3 text-amber-400">{result.quantum_metrics.inference_time_seconds}s</td>
                      {result.hybrid_metrics && (
                        <td className="py-2.5 px-3 text-amber-300">{result.hybrid_metrics.inference_time_seconds}s</td>
                      )}
                    </tr>
                  </tbody>
                </table>
              </div>

              {/* End-to-End Pipeline Execution Breakdown */}
              {result.pipeline_breakdown && (
                <div className="p-4 rounded-xl bg-slate-900/80 border border-white/10 flex flex-col gap-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-white flex items-center space-x-2">
                      <Clock className="w-4 h-4 text-amber-400" />
                      <span>Pipeline Wall-Clock Latency Breakdown</span>
                    </span>
                    <span className="text-xs font-mono text-amber-400 font-bold">
                      Total: {result.pipeline_breakdown.total_ms} ms
                    </span>
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                    <div className="p-2.5 rounded-lg bg-slate-950 border border-white/5">
                      <div className="text-[10px] uppercase text-slate-500 font-semibold">Classical Extraction</div>
                      <div className="text-sm font-mono font-bold text-emerald-400">{result.pipeline_breakdown.classical_ms} ms</div>
                    </div>
                    <div className="p-2.5 rounded-lg bg-slate-950 border border-white/5">
                      <div className="text-[10px] uppercase text-slate-500 font-semibold">Quantum Simulation</div>
                      <div className="text-sm font-mono font-bold text-quantum-300">{result.pipeline_breakdown.quantum_ms} ms</div>
                    </div>
                    <div className="p-2.5 rounded-lg bg-slate-950 border border-white/5">
                      <div className="text-[10px] uppercase text-slate-500 font-semibold">Mathematical Fusion</div>
                      <div className="text-sm font-mono font-bold text-amber-400">{result.pipeline_breakdown.fusion_ms} ms</div>
                    </div>
                    <div className="p-2.5 rounded-lg bg-slate-950 border border-white/5">
                      <div className="text-[10px] uppercase text-slate-500 font-semibold">Speech Recommendation</div>
                      <div className="text-sm font-mono font-bold text-indigo-400">{result.pipeline_breakdown.recommendation_ms} ms</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Speech Recommendation Card with [Apply] Action */}
              {result.speech_recommendation && (
                <div className="p-5 rounded-2xl bg-gradient-to-br from-amber-500/10 via-orange-500/5 to-purple-500/10 border border-amber-500/30 flex flex-col gap-4">
                  <div className="flex items-center justify-between border-b border-amber-500/20 pb-3">
                    <div className="flex items-center space-x-2">
                      <Volume2 className="w-5 h-5 text-amber-400" />
                      <span className="font-bold text-white text-sm">Provider-Independent Speech Recommendation</span>
                    </div>
                    <span className="text-xs px-2.5 py-0.5 rounded-full bg-amber-500/20 text-amber-300 font-mono">
                      Decoupled from ElevenLabs
                    </span>
                  </div>

                  <p className="text-xs text-slate-300 italic">
                    "{result.speech_recommendation.reason}"
                  </p>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    <div className="p-2 rounded-xl bg-slate-950/60 border border-white/5 text-center">
                      <div className="text-[10px] uppercase text-slate-400">Style</div>
                      <div className="text-sm font-bold text-amber-300 capitalize">{result.speech_recommendation.style}</div>
                    </div>
                    <div className="p-2 rounded-xl bg-slate-950/60 border border-white/5 text-center">
                      <div className="text-[10px] uppercase text-slate-400">Pacing</div>
                      <div className="text-sm font-bold text-amber-300 capitalize">{result.speech_recommendation.pacing}</div>
                    </div>
                    <div className="p-2 rounded-xl bg-slate-950/60 border border-white/5 text-center">
                      <div className="text-[10px] uppercase text-slate-400">Speed Multiplier</div>
                      <div className="text-sm font-bold text-white font-mono">{result.speech_recommendation.speed}x</div>
                    </div>
                    <div className="p-2 rounded-xl bg-slate-950/60 border border-white/5 text-center">
                      <div className="text-[10px] uppercase text-slate-400">Stability</div>
                      <div className="text-sm font-bold text-white font-mono">{result.speech_recommendation.stability}</div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-2">
                    <div className="text-[11px] text-slate-400">
                      User Autonomy: settings will only apply if explicitly confirmed.
                    </div>
                    <button
                      onClick={() => handleApplyToTTS(result.speech_recommendation!)}
                      className="px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs flex items-center space-x-1.5 shadow-lg shadow-amber-500/20 transition"
                    >
                      <span>Apply Settings to Speech Studio</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              )}

              {/* Honest Technical Analysis Callout */}
              <div className="p-4 rounded-xl bg-slate-950/80 border border-amber-500/20 flex flex-col gap-2">
                <div className="flex items-center space-x-2 text-amber-400 text-xs font-bold">
                  <Info className="w-4 h-4 shrink-0" />
                  <span>Honest Technical Analysis (No Fabricated Advantage Claims)</span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed font-sans">
                  {result.honest_analysis}
                </p>
              </div>
            </div>
          ) : (
            <div className="glass-panel rounded-2xl p-16 text-center border border-white/10 text-slate-400 flex flex-col items-center justify-center gap-3">
              <BarChart2 className="w-12 h-12 text-slate-600" />
              <p className="text-base font-semibold text-white">Benchmark Awaiting Execution</p>
              <p className="text-xs text-slate-500 max-w-md leading-relaxed">
                Select a benchmark category and click "Execute Benchmark" to run empirical comparisons between classical algorithms and quantum intelligence circuits.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
