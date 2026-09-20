import React from 'react';
import { Trash2, Sparkles, AlertCircle, Clock, Hash, FileText } from 'lucide-react';
import { useWorkspaceStore } from '../../stores/workspaceStore';

const PRESET_SAMPLES = [
  {
    label: 'Standard Introduction',
    text: 'Hello and welcome to Bloop! This is an intermediate full-stack text-to-speech platform powered by dynamic voice orchestration and educational quantum computing algorithms.',
  },
  {
    label: 'Audiobook Narration',
    text: 'The evening mist settled quietly over the valley as the distant bell echoed three times through the damp pines, signaling that the journey had only just begun.',
  },
  {
    label: 'Technical Briefing',
    text: 'All API endpoints are versioned under /api/v1. The system utilizes PostgreSQL for relational integrity, while quantum statevector simulations compute kernel fidelity without blocking the core speech pipeline.',
  },
];

export const TextInputArea: React.FC = () => {
  const { text, stats, setText, clearText, loadSample } = useWorkspaceStore();

  const maxChars = 2500;
  const isOverLimit = stats.char_count > maxChars;
  const percentageUsed = Math.min((stats.char_count / maxChars) * 100, 100);

  return (
    <div className="glass-panel rounded-2xl p-5 border border-white/10 flex flex-col gap-4 shadow-xl">
      {/* Header and Preset Samples */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-white/5 pb-3">
        <div className="flex items-center space-x-2">
          <FileText className="w-5 h-5 text-bloop-400" />
          <h2 className="text-base font-semibold text-white">Enter or Paste Text</h2>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-xs text-slate-400 hidden sm:inline">Presets:</span>
          {PRESET_SAMPLES.map((sample, idx) => (
            <button
              key={idx}
              onClick={() => loadSample(sample.text)}
              className="px-2.5 py-1 rounded-md text-xs bg-slate-800/80 hover:bg-bloop-600/30 hover:text-bloop-300 text-slate-300 border border-white/5 transition"
            >
              <Sparkles className="w-3 h-3 inline mr-1 text-bloop-400" />
              {sample.label}
            </button>
          ))}
          {text && (
            <button
              onClick={clearText}
              title="Clear text"
              className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-md transition"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Main Textarea */}
      <div className="relative">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Type or paste the words you want to synthesize into speech..."
          rows={7}
          className={`w-full bg-slate-950/60 text-slate-100 text-base rounded-xl p-4 border focus:outline-none transition resize-none placeholder-slate-500 leading-relaxed font-sans ${
            isOverLimit
              ? 'border-rose-500 focus:border-rose-400'
              : 'border-white/10 focus:border-bloop-500/80 focus:ring-1 focus:ring-bloop-500/50'
          }`}
        />
      </div>

      {/* Counters & Limits Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 text-xs pt-1">
        <div className="flex items-center space-x-4 text-slate-400 font-medium">
          <span className="flex items-center space-x-1">
            <Hash className="w-3.5 h-3.5 text-bloop-400" />
            <span className={isOverLimit ? 'text-rose-400 font-bold' : 'text-slate-200'}>
              {stats.char_count.toLocaleString()}
            </span>
            <span>/ {maxChars.toLocaleString()} characters</span>
          </span>

          <span className="flex items-center space-x-1">
            <span className="text-slate-200 font-bold">{stats.word_count.toLocaleString()}</span>
            <span>words</span>
          </span>

          <span className="flex items-center space-x-1 hidden sm:flex">
            <Clock className="w-3.5 h-3.5 text-quantum-400" />
            <span>~{stats.estimated_duration_seconds}s estimated audio</span>
          </span>
        </div>

        {/* Progress Bar for Char Limit */}
        <div className="w-32 bg-slate-800 rounded-full h-2 overflow-hidden">
          <div
            className={`h-full transition-all duration-200 ${
              isOverLimit ? 'bg-rose-500' : percentageUsed > 80 ? 'bg-amber-500' : 'bg-bloop-500'
            }`}
            style={{ width: `${percentageUsed}%` }}
          />
        </div>
      </div>

      {isOverLimit && (
        <div className="flex items-center space-x-2 text-xs text-rose-400 bg-rose-500/10 border border-rose-500/30 rounded-lg p-2.5">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>Text exceeds the maximum allowed limit of 2,500 characters. Please shorten your text.</span>
        </div>
      )}
    </div>
  );
};
