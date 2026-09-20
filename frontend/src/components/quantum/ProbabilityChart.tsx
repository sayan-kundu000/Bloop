import React from 'react';

interface ProbabilityChartProps {
  probabilities: Record<string, number>;
  title?: string;
}

export const ProbabilityChart: React.FC<ProbabilityChartProps> = ({
  probabilities,
  title = 'Measurement State Probabilities',
}) => {
  const entries = Object.entries(probabilities).sort((a, b) => b[1] - a[1]);

  return (
    <div className="flex flex-col gap-2.5 p-4 rounded-xl bg-slate-950/70 border border-white/10 font-mono text-xs">
      <div className="flex items-center justify-between border-b border-white/5 pb-2">
        <span className="font-semibold text-slate-300 font-sans">{title}</span>
        <span className="text-slate-500 text-[10px]">Basis States |x⟩</span>
      </div>

      <div className="flex flex-col gap-2 pt-1">
        {entries.map(([state, prob]) => {
          const percent = Math.round(prob * 1000) / 10;
          return (
            <div key={state} className="flex items-center space-x-3">
              <span className="w-16 font-bold text-quantum-300 shrink-0 text-left">
                {state.startsWith('|') ? state : `|${state}⟩`}
              </span>

              <div className="w-full bg-slate-800 rounded-full h-3 overflow-hidden relative">
                <div
                  className="h-full bg-gradient-to-r from-bloop-500 to-quantum-500 transition-all duration-500"
                  style={{ width: `${Math.max(percent, 1)}%` }}
                />
              </div>

              <span className="w-12 text-right text-slate-300 shrink-0 font-medium">
                {percent}%
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
