import React from 'react';
import { NavLink } from 'react-router-dom';
import { Atom, FileText, Heart, GitCompare, Cpu, BarChart2 } from 'lucide-react';

export const QuantumNav: React.FC = () => {
  const tabs = [
    { to: '/quantum', end: true, label: 'Overview', icon: Atom },
    { to: '/quantum/text', label: 'Text Intelligence', icon: FileText },
    { to: '/quantum/emotion', label: 'Emotion QNN', icon: Heart },
    { to: '/quantum/semantic', label: 'Semantic Kernel', icon: GitCompare },
    { to: '/quantum/circuits', label: 'Circuit Sandbox', icon: Cpu },
    { to: '/quantum/benchmark', label: 'Benchmarking', icon: BarChart2 },
  ];

  return (
    <div className="flex items-center space-x-1.5 p-1.5 rounded-xl glass-panel border border-white/10 overflow-x-auto mb-6">
      {tabs.map((tab) => {
        const Icon = tab.icon;
        return (
          <NavLink
            key={tab.to}
            to={tab.to}
            end={tab.end}
            className={({ isActive }) =>
              `flex items-center space-x-2 px-3.5 py-2 rounded-lg text-xs font-semibold whitespace-nowrap transition-all duration-150 ${
                isActive
                  ? 'bg-quantum-600/30 text-quantum-300 border border-quantum-500/50 shadow-md shadow-quantum-600/20'
                  : 'text-slate-400 hover:text-white hover:bg-white/5'
              }`
            }
          >
            <Icon className="w-3.5 h-3.5 text-quantum-400" />
            <span>{tab.label}</span>
          </NavLink>
        );
      })}
    </div>
  );
};
