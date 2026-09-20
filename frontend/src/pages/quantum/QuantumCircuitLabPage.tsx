import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import {
  Cpu,
  Play,
  Trash2,
  Clock,
  Activity,
  Layers,
  ShieldAlert,
  Sliders,
  BarChart2,
  TrendingDown,
  Info,
  ChevronRight,
  Code,
} from 'lucide-react';
import { QuantumNav } from '../../components/quantum/QuantumNav';
import { ProbabilityChart } from '../../components/quantum/ProbabilityChart';
import { quantumApi } from '../../api/client';
import {
  GateOperation,
  QuantumCircuitResult,
  CircuitComparisonResult,
  CircuitRobustnessResult,
} from '../../types';

type LabTab = 'simulate' | 'compare' | 'robustness';

const PRESET_CIRCUITS = [
  {
    id: 'bell_state',
    name: 'Bell State (|Φ⁺⟩)',
    qubits: 2,
    gates: [
      { gate: 'h', target: 0 },
      { gate: 'cx', control: 0, target: 1 },
    ],
  },
  {
    id: 'ghz_state',
    name: 'GHZ State (3 Qubits)',
    qubits: 3,
    gates: [
      { gate: 'h', target: 0 },
      { gate: 'cx', control: 0, target: 1 },
      { gate: 'cx', control: 1, target: 2 },
    ],
  },
  {
    id: 'superposition_4q',
    name: 'Superposition (4Q)',
    qubits: 4,
    gates: [
      { gate: 'h', target: 0 },
      { gate: 'h', target: 1 },
      { gate: 'h', target: 2 },
      { gate: 'h', target: 3 },
    ],
  },
  {
    id: 'rotation_experiment',
    name: 'Rotation Interference',
    qubits: 1,
    gates: [
      { gate: 'h', target: 0 },
      { gate: 'ry', target: 0, parameter: 1.047 },
      { gate: 'h', target: 0 },
    ],
  },
  {
    id: 'entanglement_experiment',
    name: 'Entanglement & Parity',
    qubits: 2,
    gates: [
      { gate: 'h', target: 0 },
      { gate: 'cx', control: 0, target: 1 },
      { gate: 'rz', target: 1, parameter: 0.785 },
    ],
  },
];

export const QuantumCircuitLabPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<LabTab>('simulate');
  const [numQubits, setNumQubits] = useState(2);
  const [gates, setGates] = useState<GateOperation[]>([
    { gate: 'h', target: 0 },
    { gate: 'cx', control: 0, target: 1 },
  ]);
  const [shots, setShots] = useState(1024);
  const [noiseProfile, setNoiseProfile] = useState('ideal');
  const [noiseModel, setNoiseModel] = useState('depolarizing');

  // New Gate Composer States
  const [newGate, setNewGate] = useState('h');
  const [newTarget, setNewTarget] = useState(0);
  const [newControl, setNewControl] = useState(1);
  const [newParameter, setNewParameter] = useState('1.571');

  // Sweep States for Mode D
  const [sweepStart, setSweepStart] = useState(0.0);
  const [sweepStop, setSweepStop] = useState(0.08);
  const [sweepStep, setSweepStep] = useState(0.02);

  // Result States
  const [simResult, setSimResult] = useState<QuantumCircuitResult | null>(null);
  const [compResult, setCompResult] = useState<CircuitComparisonResult | null>(null);
  const [robResult, setRobResult] = useState<CircuitRobustnessResult | null>(null);

  // Mutations
  const simMutation = useMutation({
    mutationFn: quantumApi.executeCircuit,
    onSuccess: (data) => setSimResult(data),
  });

  const compMutation = useMutation({
    mutationFn: quantumApi.compareCircuits,
    onSuccess: (data) => setCompResult(data),
  });

  const robMutation = useMutation({
    mutationFn: quantumApi.runRobustness,
    onSuccess: (data) => setRobResult(data),
  });

  const isPending = simMutation.isPending || compMutation.isPending || robMutation.isPending;
  const currentError = simMutation.error || compMutation.error || robMutation.error;

  const handleAddGate = () => {
    const is2Qubit = ['cx', 'cz', 'swap'].includes(newGate);
    const isParam = ['rx', 'ry', 'rz'].includes(newGate);
    const op: GateOperation = {
      gate: newGate,
      target: newTarget,
      control: is2Qubit ? newControl : undefined,
      parameter: isParam ? parseFloat(newParameter) || 1.571 : undefined,
    };
    setGates([...gates, op]);
  };

  const handleRemoveGate = (index: number) => {
    setGates(gates.filter((_, i) => i !== index));
  };

  const handleApplyPreset = (preset: typeof PRESET_CIRCUITS[0]) => {
    setNumQubits(preset.qubits);
    setGates([...preset.gates]);
  };

  const handleRun = () => {
    if (activeTab === 'simulate') {
      simMutation.mutate({
        num_qubits: numQubits,
        gates,
        shots,
        noise_profile: noiseProfile !== 'ideal' ? noiseProfile : undefined,
      });
    } else if (activeTab === 'compare') {
      compMutation.mutate({
        num_qubits: numQubits,
        gates,
        shots,
        noise_profile: noiseProfile !== 'ideal' ? noiseProfile : 'medium_noise',
      });
    } else if (activeTab === 'robustness') {
      robMutation.mutate({
        num_qubits: numQubits,
        gates,
        shots: Math.min(shots, 2048),
        noise_model: noiseModel,
        sweep: {
          parameter: 'probability',
          start: sweepStart,
          stop: sweepStop,
          step: sweepStep,
        },
        repeats_per_point: 1,
      });
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-gradient-to-br from-fuchsia-600/20 to-quantum-600/20 border border-fuchsia-500/30 text-fuchsia-400">
            <Cpu className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-3xl font-extrabold text-white tracking-tight">
              Quantum Circuit & <span className="gradient-text-quantum">Noise Laboratory</span>
            </h1>
            <p className="text-sm text-slate-400 mt-0.5">
              Experiment with bounded quantum circuits, inject controlled decoherence noise models, compare ideal vs. noisy simulations, and execute parameter robustness sweeps.
            </p>
          </div>
        </div>
      </div>

      <QuantumNav />

      {/* Mode Navigation Tabs */}
      <div className="flex space-x-2 border-b border-white/10 pb-4 mb-6">
        <button
          onClick={() => setActiveTab('simulate')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold transition ${
            activeTab === 'simulate'
              ? 'bg-quantum-600 text-white shadow-lg shadow-quantum-600/20'
              : 'bg-slate-900/60 text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          <Play className="w-4 h-4" />
          <span>Mode A/B: Simulation</span>
        </button>

        <button
          onClick={() => setActiveTab('compare')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold transition ${
            activeTab === 'compare'
              ? 'bg-fuchsia-600 text-white shadow-lg shadow-fuchsia-600/20'
              : 'bg-slate-900/60 text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          <BarChart2 className="w-4 h-4" />
          <span>Mode C: Ideal vs Noisy Comparison</span>
        </button>

        <button
          onClick={() => setActiveTab('robustness')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold transition ${
            activeTab === 'robustness'
              ? 'bg-amber-600 text-white shadow-lg shadow-amber-600/20'
              : 'bg-slate-900/60 text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          <TrendingDown className="w-4 h-4" />
          <span>Mode D: Robustness Sweep</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Circuit Composer & Controls (5 cols) */}
        <div className="lg:col-span-5 flex flex-col gap-6">
          <div className="glass-panel rounded-2xl p-6 border border-white/10 shadow-xl flex flex-col gap-5">
            {/* Presets */}
            <div>
              <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider block mb-2">
                Deterministic Circuit Templates
              </span>
              <div className="flex flex-wrap gap-2">
                {PRESET_CIRCUITS.map((preset) => (
                  <button
                    key={preset.id}
                    onClick={() => handleApplyPreset(preset)}
                    className="px-2.5 py-1 rounded-lg text-xs bg-slate-900 border border-white/10 hover:border-quantum-500 text-slate-200 transition"
                  >
                    {preset.name}
                  </button>
                ))}
              </div>
            </div>

            {/* Qubit Count & Shots */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Qubit Register
                </label>
                <select
                  value={numQubits}
                  onChange={(e) => setNumQubits(parseInt(e.target.value))}
                  className="w-full bg-slate-900 text-sm text-white rounded-xl p-2.5 border border-white/10 focus:outline-none focus:border-quantum-500"
                >
                  {[1, 2, 3, 4, 5, 6].map((q) => (
                    <option key={q} value={q}>
                      {q} {q === 1 ? 'Qubit' : 'Qubits'}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Shots: {shots}
                </label>
                <select
                  value={shots}
                  onChange={(e) => setShots(parseInt(e.target.value))}
                  className="w-full bg-slate-900 text-sm text-white rounded-xl p-2.5 border border-white/10 focus:outline-none focus:border-quantum-500"
                >
                  <option value={512}>512 Shots</option>
                  <option value={1024}>1024 Shots</option>
                  <option value={2048}>2048 Shots</option>
                  <option value={4096}>4096 Shots</option>
                </select>
              </div>
            </div>

            {/* Noise Environment Configuration */}
            {activeTab !== 'robustness' ? (
              <div className="p-4 rounded-xl bg-slate-950/70 border border-white/10 flex flex-col gap-2.5">
                <span className="text-xs font-semibold text-slate-300 flex items-center space-x-1.5">
                  <Sliders className="w-3.5 h-3.5 text-quantum-400" />
                  <span>
                    {activeTab === 'simulate' ? 'Simulated Noise Channel' : 'Comparison Noise Model'}
                  </span>
                </span>
                <select
                  value={noiseProfile}
                  onChange={(e) => setNoiseProfile(e.target.value)}
                  className="w-full bg-slate-900 text-xs text-white rounded-lg p-2.5 border border-white/10 focus:border-quantum-500"
                >
                  <option value="ideal">Ideal (Zero Noise)</option>
                  <option value="low_noise">Low Noise (Depolarizing p=0.005, Readout=1%)</option>
                  <option value="medium_noise">Medium Noise (Depolarizing p=0.02, Readout=3%)</option>
                  <option value="high_noise">High Noise (Depolarizing p=0.06, Readout=6%)</option>
                </select>
              </div>
            ) : (
              <div className="p-4 rounded-xl bg-slate-950/70 border border-white/10 flex flex-col gap-3">
                <span className="text-xs font-semibold text-amber-400 flex items-center space-x-1.5">
                  <TrendingDown className="w-3.5 h-3.5" />
                  <span>Noise Sweep Parameter Range</span>
                </span>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <label className="block text-slate-400 mb-1">Noise Channel</label>
                    <select
                      value={noiseModel}
                      onChange={(e) => setNoiseModel(e.target.value)}
                      className="w-full bg-slate-900 text-white rounded-lg p-2 border border-white/10"
                    >
                      <option value="depolarizing">Depolarizing</option>
                      <option value="bit_flip">Bit-Flip (X)</option>
                      <option value="phase_flip">Phase-Flip (Z)</option>
                      <option value="readout_error">Readout Error</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-slate-400 mb-1">Step Increment</label>
                    <select
                      value={sweepStep}
                      onChange={(e) => setSweepStep(parseFloat(e.target.value))}
                      className="w-full bg-slate-900 text-white rounded-lg p-2 border border-white/10"
                    >
                      <option value={0.01}>0.01 (Fine)</option>
                      <option value={0.02}>0.02 (Standard)</option>
                      <option value={0.03}>0.03 (Coarse)</option>
                    </select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <label className="block text-slate-400 mb-1">Start Prob: {sweepStart}</label>
                    <input
                      type="range"
                      min="0.0"
                      max="0.04"
                      step="0.01"
                      value={sweepStart}
                      onChange={(e) => setSweepStart(parseFloat(e.target.value))}
                      className="w-full accent-amber-500"
                    />
                  </div>
                  <div>
                    <label className="block text-slate-400 mb-1">Stop Prob: {sweepStop}</label>
                    <input
                      type="range"
                      min="0.04"
                      max="0.10"
                      step="0.01"
                      value={sweepStop}
                      onChange={(e) => setSweepStop(parseFloat(e.target.value))}
                      className="w-full accent-amber-500"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Add Gate Tool */}
            <div className="p-4 rounded-xl bg-slate-950/70 border border-white/10 flex flex-col gap-3">
              <span className="text-xs font-semibold text-white">Add Quantum Gate</span>
              <div className="grid grid-cols-3 gap-2 text-xs">
                <div>
                  <label className="block text-slate-400 mb-1">Gate</label>
                  <select
                    value={newGate}
                    onChange={(e) => setNewGate(e.target.value)}
                    className="w-full bg-slate-900 text-white rounded-lg p-2 border border-white/10"
                  >
                    <optgroup label="Single-Qubit">
                      <option value="h">H (Hadamard)</option>
                      <option value="x">X (Pauli-X)</option>
                      <option value="y">Y (Pauli-Y)</option>
                      <option value="z">Z (Pauli-Z)</option>
                      <option value="s">S (Phase π/2)</option>
                      <option value="t">T (Phase π/4)</option>
                    </optgroup>
                    <optgroup label="Rotations">
                      <option value="rx">RX(θ)</option>
                      <option value="ry">RY(θ)</option>
                      <option value="rz">RZ(θ)</option>
                    </optgroup>
                    <optgroup label="Two-Qubit">
                      <option value="cx">CX (CNOT)</option>
                      <option value="cz">CZ</option>
                      <option value="swap">SWAP</option>
                    </optgroup>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-400 mb-1">Target</label>
                  <select
                    value={newTarget}
                    onChange={(e) => setNewTarget(parseInt(e.target.value))}
                    className="w-full bg-slate-900 text-white rounded-lg p-2 border border-white/10"
                  >
                    {Array.from({ length: numQubits }).map((_, i) => (
                      <option key={i} value={i}>
                        q[{i}]
                      </option>
                    ))}
                  </select>
                </div>

                {['cx', 'cz', 'swap'].includes(newGate) ? (
                  <div>
                    <label className="block text-slate-400 mb-1">Control</label>
                    <select
                      value={newControl}
                      onChange={(e) => setNewControl(parseInt(e.target.value))}
                      className="w-full bg-slate-900 text-white rounded-lg p-2 border border-white/10"
                    >
                      {Array.from({ length: numQubits }).map((_, i) => (
                        <option key={i} value={i}>
                          q[{i}]
                        </option>
                      ))}
                    </select>
                  </div>
                ) : ['rx', 'ry', 'rz'].includes(newGate) ? (
                  <div>
                    <label className="block text-slate-400 mb-1">Angle θ</label>
                    <input
                      type="text"
                      value={newParameter}
                      onChange={(e) => setNewParameter(e.target.value)}
                      className="w-full bg-slate-900 text-white rounded-lg p-2 border border-white/10"
                      placeholder="1.571"
                    />
                  </div>
                ) : (
                  <div className="flex items-end">
                    <button
                      type="button"
                      onClick={handleAddGate}
                      className="w-full py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-xs font-semibold"
                    >
                      + Add Gate
                    </button>
                  </div>
                )}
              </div>

              {(['cx', 'cz', 'swap'].includes(newGate) || ['rx', 'ry', 'rz'].includes(newGate)) && (
                <button
                  type="button"
                  onClick={handleAddGate}
                  className="w-full py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-xs font-semibold mt-1"
                >
                  + Append Operation
                </button>
              )}
            </div>

            {/* Current Gate Sequence */}
            <div>
              <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
                <span>Gate Sequence ({gates.length} operations)</span>
                {gates.length > 0 && (
                  <button
                    onClick={() => setGates([])}
                    className="text-rose-400 hover:underline text-[11px]"
                  >
                    Clear All
                  </button>
                )}
              </div>

              <div className="flex flex-wrap gap-2 max-h-36 overflow-y-auto pr-1">
                {gates.map((g, idx) => (
                  <div
                    key={idx}
                    className="flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-slate-900 border border-white/10 text-xs font-mono text-white"
                  >
                    <span className="font-bold uppercase text-quantum-400">{g.gate}</span>
                    <span className="text-slate-400">
                      {g.control !== undefined
                        ? `q[${g.control}]→q[${g.target}]`
                        : g.parameter !== undefined
                        ? `q[${g.target}](θ=${g.parameter.toFixed(2)})`
                        : `q[${g.target}]`}
                    </span>
                    <button
                      onClick={() => handleRemoveGate(idx)}
                      className="text-slate-500 hover:text-rose-400 ml-1 font-sans"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* Run Button */}
            <button
              onClick={handleRun}
              disabled={isPending}
              className="mt-2 w-full py-3.5 rounded-xl bg-gradient-to-r from-fuchsia-600 via-quantum-600 to-bloop-600 hover:opacity-95 text-white font-semibold text-sm shadow-lg shadow-fuchsia-600/20 flex items-center justify-center space-x-2 transition"
            >
              {isPending ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>
                    {activeTab === 'simulate'
                      ? 'Simulating on Aer...'
                      : activeTab === 'compare'
                      ? 'Executing Comparative Experiment...'
                      : 'Running Robustness Parameter Sweep...'}
                  </span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-current" />
                  <span>
                    {activeTab === 'simulate'
                      ? 'Simulate Circuit'
                      : activeTab === 'compare'
                      ? 'Run Ideal vs Noisy Comparison'
                      : 'Run Robustness Sweep'}
                  </span>
                </>
              )}
            </button>

            {currentError && (
              <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center space-x-2">
                <ShieldAlert className="w-4 h-4 shrink-0 text-rose-400" />
                <span>Execution error: {(currentError as any)?.message || 'Failed to simulate'}</span>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Visualization Results (7 cols) */}
        <div className="lg:col-span-7 flex flex-col gap-6">
          {/* MODE A / B: SINGLE SIMULATION RESULTS */}
          {activeTab === 'simulate' && simResult && (
            <div className="glass-panel rounded-2xl p-6 border border-white/10 shadow-xl flex flex-col gap-5">
              <div className="flex items-center justify-between border-b border-white/10 pb-3">
                <div className="flex items-center space-x-2">
                  <span className="font-bold text-white text-base">Aer Simulation Results</span>
                  {simResult.is_noisy_simulation ? (
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30 font-mono">
                      Noisy ({simResult.noise_model || 'Decoherence'})
                    </span>
                  ) : (
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-mono">
                      Ideal (Zero Noise)
                    </span>
                  )}
                </div>
                <span className="text-xs text-slate-400 font-mono flex items-center space-x-1">
                  <Clock className="w-3.5 h-3.5" />
                  <span>{simResult.execution_time_ms} ms</span>
                </span>
              </div>

              {/* Entropy & Dominant State Badges */}
              <div className="grid grid-cols-3 gap-3">
                <div className="p-3 rounded-xl bg-slate-900/60 border border-white/5">
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Circuit Depth</span>
                  <span className="text-lg font-bold text-white font-mono">{simResult.circuit_depth}</span>
                </div>
                <div className="p-3 rounded-xl bg-slate-900/60 border border-white/5">
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Shannon Entropy</span>
                  <span className="text-lg font-bold text-quantum-300 font-mono">
                    {simResult.entropy !== undefined ? `${simResult.entropy} bits` : 'N/A'}
                  </span>
                </div>
                <div className="p-3 rounded-xl bg-slate-900/60 border border-white/5">
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Dominant State</span>
                  <span className="text-lg font-bold text-fuchsia-300 font-mono">
                    |{simResult.dominant_state || '0'}⟩
                  </span>
                </div>
              </div>

              {/* Wire Diagram */}
              <div>
                <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider block mb-2">
                  Circuit Wire Diagram
                </span>
                <pre className="p-4 rounded-xl bg-black/90 border border-white/10 text-emerald-400 text-xs font-mono overflow-x-auto leading-tight shadow-inner">
                  {simResult.circuit_diagram_ascii}
                </pre>
              </div>

              {/* Measurement Distribution */}
              <ProbabilityChart
                probabilities={simResult.probabilities}
                title="Measured Basis State Probabilities"
              />

              {/* OpenQASM */}
              <div>
                <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider block mb-2">
                  OpenQASM 2.0 Export
                </span>
                <pre className="p-3 rounded-xl bg-slate-950/80 border border-white/10 text-slate-300 text-[11px] font-mono overflow-x-auto max-h-32">
                  {simResult.qasm}
                </pre>
              </div>
            </div>
          )}

          {/* MODE C: COMPARISON RESULTS */}
          {activeTab === 'compare' && compResult && (
            <div className="glass-panel rounded-2xl p-6 border border-white/10 shadow-xl flex flex-col gap-5">
              <div className="flex items-center justify-between border-b border-white/10 pb-3">
                <div className="flex items-center space-x-2">
                  <span className="font-bold text-white text-base">Ideal vs Noisy Comparison</span>
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-fuchsia-500/20 text-fuchsia-300 border border-fuchsia-500/30 font-mono">
                    {compResult.noise_model}
                  </span>
                </div>
                <span className="text-xs text-slate-400 font-mono flex items-center space-x-1">
                  <Clock className="w-3.5 h-3.5" />
                  <span>{compResult.execution_time_ms} ms</span>
                </span>
              </div>

              {/* Metrics Gauges */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="p-3 rounded-xl bg-slate-900/80 border border-white/5 flex flex-col">
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider">Total Var Distance</span>
                  <span className="text-lg font-bold text-amber-300 font-mono mt-1">
                    {compResult.total_variation_distance}
                  </span>
                  <span className="text-[10px] text-slate-500 mt-0.5">TVD ∈ [0, 1]</span>
                </div>

                <div className="p-3 rounded-xl bg-slate-900/80 border border-white/5 flex flex-col">
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider">Classical Fidelity</span>
                  <span className="text-lg font-bold text-emerald-300 font-mono mt-1">
                    {compResult.classical_fidelity}
                  </span>
                  <span className="text-[10px] text-slate-500 mt-0.5">Bhattacharyya F</span>
                </div>

                <div className="p-3 rounded-xl bg-slate-900/80 border border-white/5 flex flex-col">
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider">Ideal Entropy</span>
                  <span className="text-lg font-bold text-quantum-300 font-mono mt-1">
                    {compResult.ideal_entropy}
                  </span>
                  <span className="text-[10px] text-slate-500 mt-0.5">bits</span>
                </div>

                <div className="p-3 rounded-xl bg-slate-900/80 border border-white/5 flex flex-col">
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider">Noisy Entropy</span>
                  <span className="text-lg font-bold text-fuchsia-300 font-mono mt-1">
                    {compResult.noisy_entropy}
                  </span>
                  <span className="text-[10px] text-slate-500 mt-0.5">bits (decoherence)</span>
                </div>
              </div>

              {/* Side-by-Side State Distribution Table */}
              <div>
                <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider block mb-2">
                  Discrete State Distribution Comparison
                </span>
                <div className="overflow-x-auto rounded-xl border border-white/10 bg-slate-950/70">
                  <table className="w-full text-xs font-mono text-left">
                    <thead className="bg-slate-900/80 text-slate-400 border-b border-white/10">
                      <tr>
                        <th className="py-2.5 px-3">State |x⟩</th>
                        <th className="py-2.5 px-3 text-emerald-400">Ideal Prob</th>
                        <th className="py-2.5 px-3 text-fuchsia-400">Noisy Prob</th>
                        <th className="py-2.5 px-3 text-amber-300">Divergence |Δ|</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                      {compResult.states_comparison.map((row) => (
                        <tr key={row.state} className="hover:bg-slate-900/40">
                          <td className="py-2 px-3 font-bold text-white">|{row.state}⟩</td>
                          <td className="py-2 px-3 text-emerald-300">
                            {(row.ideal_probability * 100).toFixed(1)}%
                          </td>
                          <td className="py-2 px-3 text-fuchsia-300">
                            {(row.noisy_probability * 100).toFixed(1)}%
                          </td>
                          <td className="py-2 px-3 text-amber-300 font-bold">
                            {(row.divergence * 100).toFixed(1)}%
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Wire Diagram */}
              <div>
                <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider block mb-2">
                  Evaluated Circuit
                </span>
                <pre className="p-3 rounded-xl bg-black/90 border border-white/10 text-emerald-400 text-xs font-mono overflow-x-auto leading-tight">
                  {compResult.circuit_diagram_ascii}
                </pre>
              </div>
            </div>
          )}

          {/* MODE D: ROBUSTNESS SWEEP RESULTS */}
          {activeTab === 'robustness' && robResult && (
            <div className="glass-panel rounded-2xl p-6 border border-white/10 shadow-xl flex flex-col gap-5">
              <div className="flex items-center justify-between border-b border-white/10 pb-3">
                <div>
                  <span className="font-bold text-white text-base">Noise Sweep Robustness Curve</span>
                  <span className="text-xs text-slate-400 block mt-0.5">
                    Tracked Target State: <span className="text-amber-300 font-mono">|{robResult.target_state}⟩</span>
                  </span>
                </div>
                <span className="text-xs text-slate-400 font-mono flex items-center space-x-1">
                  <Clock className="w-3.5 h-3.5" />
                  <span>{robResult.total_execution_time_ms} ms</span>
                </span>
              </div>

              {/* Summary Banner */}
              <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-200 flex items-start space-x-2">
                <Info className="w-4 h-4 shrink-0 text-amber-400 mt-0.5" />
                <span>{robResult.summary}</span>
              </div>

              {/* Progression Data Points Table */}
              <div>
                <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider block mb-2">
                  Empirical Sweep Observations ({robResult.points.length} levels)
                </span>
                <div className="overflow-x-auto rounded-xl border border-white/10 bg-slate-950/70">
                  <table className="w-full text-xs font-mono text-left">
                    <thead className="bg-slate-900/80 text-slate-400 border-b border-white/10">
                      <tr>
                        <th className="py-2.5 px-3">Noise Level (p)</th>
                        <th className="py-2.5 px-3 text-emerald-400">Mean Fidelity</th>
                        <th className="py-2.5 px-3 text-amber-400">Mean TVD</th>
                        <th className="py-2.5 px-3 text-quantum-300">Target Prob</th>
                        <th className="py-2.5 px-3 text-slate-400">Latency</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                      {robResult.points.map((pt, idx) => (
                        <tr key={idx} className="hover:bg-slate-900/40">
                          <td className="py-2 px-3 font-bold text-white">{pt.parameter_value.toFixed(3)}</td>
                          <td className="py-2 px-3 text-emerald-300">{pt.mean_fidelity.toFixed(4)}</td>
                          <td className="py-2 px-3 text-amber-300">{pt.mean_tvd.toFixed(4)}</td>
                          <td className="py-2 px-3 text-quantum-300">
                            {(pt.success_probability * 100).toFixed(1)}%
                          </td>
                          <td className="py-2 px-3 text-slate-400">{pt.execution_time_ms} ms</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Empty Placeholder */}
          {((activeTab === 'simulate' && !simResult) ||
            (activeTab === 'compare' && !compResult) ||
            (activeTab === 'robustness' && !robResult)) && (
            <div className="glass-panel rounded-2xl p-12 text-center border border-white/10 text-slate-400 flex flex-col items-center justify-center gap-3 min-h-[400px]">
              <Cpu className="w-12 h-12 text-slate-600" />
              <p className="text-base font-semibold text-white">
                {activeTab === 'simulate'
                  ? 'Circuit Ready for Simulation'
                  : activeTab === 'compare'
                  ? 'Ready for Comparative Experiment'
                  : 'Ready for Noise Parameter Sweep'}
              </p>
              <p className="text-xs text-slate-500 max-w-md">
                {activeTab === 'simulate'
                  ? 'Compose gates on the left and select an optional noise environment to inspect measured state probabilities.'
                  : activeTab === 'compare'
                  ? 'Configure circuit and noise model to execute simultaneous ideal and noisy simulations and inspect TVD and fidelity metrics.'
                  : 'Configure noise sweep range and step size to measure fidelity decay and target-state survival probabilities.'}
              </p>
            </div>
          )}

          {/* Scientific Limitations & Educational Note */}
          <div className="p-4 rounded-xl bg-slate-900/60 border border-white/5 text-xs text-slate-400 flex items-start space-x-2.5">
            <Info className="w-4 h-4 shrink-0 text-quantum-400 mt-0.5" />
            <div>
              <span className="font-semibold text-white block mb-0.5">Scientific Principles & Simulator Transparency</span>
              <p className="text-[11px] leading-relaxed text-slate-400">
                Simulations are performed classically using Qiskit AerSimulator. Measured distributions reflect finite-shot sampling statistics rather than hardware claims. Classical distribution similarity (Bhattacharyya coefficient) evaluates computational basis overlap and is distinct from complex quantum state fidelity (|⟨ψ|φ⟩|²).
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
