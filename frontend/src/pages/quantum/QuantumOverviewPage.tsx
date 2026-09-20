import React from 'react';
import { Link } from 'react-router-dom';
import { Atom, FileText, Heart, GitCompare, Cpu, BarChart2, ArrowRight, ShieldCheck } from 'lucide-react';
import { QuantumNav } from '../../components/quantum/QuantumNav';

export const QuantumOverviewPage: React.FC = () => {
  const modules = [
    {
      to: '/quantum/text',
      title: 'Quantum Text Intelligence',
      icon: FileText,
      color: 'from-blue-600 to-indigo-600',
      description:
        'Encodes lexical feature vectors onto Qiskit multi-qubit states using angle rotations and classifies text style using a Variational Quantum Classifier (VQC).',
      badge: 'Qiskit Aer Simulator',
    },
    {
      to: '/quantum/emotion',
      title: 'Quantum Emotion Intelligence',
      icon: Heart,
      color: 'from-purple-600 to-pink-600',
      description:
        'Uses PennyLane hybrid quantum neural network circuits and multi-qubit entanglement to compute affective valence across Joy, Sadness, Anger, and Neutrality.',
      badge: 'PennyLane QNN',
    },
    {
      to: '/quantum/semantic',
      title: 'Quantum Semantic Similarity',
      icon: GitCompare,
      color: 'from-teal-600 to-emerald-600',
      description:
        'Computes quantum transition fidelity |⟨φ(x_A)|ψ(x_B)⟩|² using inversion circuits to detect semantic text duplication and topical overlap.',
      badge: 'Quantum Kernel Overlap',
    },
    {
      to: '/quantum/circuits',
      title: 'Quantum Circuit Sandbox',
      icon: Cpu,
      color: 'from-fuchsia-600 to-purple-600',
      description:
        'Interactive circuit composer supporting Hadamard, Pauli, Rotations, CNOT, CZ, and SWAP gates with both ideal statevector and noisy decoherence simulation.',
      badge: 'Custom Circuit Lab',
    },
    {
      to: '/quantum/benchmark',
      title: 'Quantum vs Classical Benchmarking',
      icon: BarChart2,
      color: 'from-amber-600 to-orange-600',
      description:
        'Rigorous, honest empirical comparison of Classical ML (Logistic Regression) vs Variational Quantum Classifiers across Accuracy, F1, runtime latency, and simulation overhead.',
      badge: 'Empirical Evaluation',
    },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center space-x-3">
          <Atom className="w-8 h-8 text-quantum-400 animate-spin-slow" />
          <span>Quantum <span className="gradient-text-quantum">Intelligence Laboratory</span></span>
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          An intermediate-level experimental suite combining quantum state representation, variational algorithms, and classical baselines.
        </p>
      </div>

      <QuantumNav />

      {/* Core Architectural Principle Alert */}
      <div className="p-4 rounded-2xl bg-gradient-to-r from-bloop-950/40 via-slate-900/80 to-quantum-950/40 border border-quantum-500/20 mb-8 flex items-start space-x-3 text-xs leading-relaxed text-slate-300">
        <ShieldCheck className="w-5 h-5 text-quantum-400 shrink-0 mt-0.5" />
        <div>
          <strong className="text-white font-semibold">Architectural Independence:</strong> Core Text-to-Speech synthesis operates completely independently from the Quantum Intelligence layer. These modules represent an educational experimentation environment built beside the speech pipeline.
        </div>
      </div>

      {/* Modules Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {modules.map((m, idx) => {
          const Icon = m.icon;
          return (
            <Link
              key={idx}
              to={m.to}
              className="glass-panel glass-panel-hover rounded-2xl p-6 border border-white/10 flex flex-col justify-between group transition duration-200"
            >
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-tr ${m.color} flex items-center justify-center shadow-lg shadow-black/40`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-white/10">
                    {m.badge}
                  </span>
                </div>

                <h3 className="text-lg font-bold text-white group-hover:text-quantum-300 transition font-['Outfit']">
                  {m.title}
                </h3>
                <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                  {m.description}
                </p>
              </div>

              <div className="pt-5 mt-5 border-t border-white/5 flex items-center justify-between text-xs font-semibold text-quantum-400 group-hover:translate-x-1 transition-transform">
                <span>Launch Laboratory</span>
                <ArrowRight className="w-4 h-4" />
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
};
