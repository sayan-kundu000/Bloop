import React from 'react';
import { Volume2, Atom, ShieldCheck, Heart } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Footer: React.FC = () => {
  return (
    <footer className="w-full border-t border-white/10 bg-slate-950/80 backdrop-blur-md mt-auto py-8 text-xs text-slate-400">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center space-x-2">
          <div className="w-6 h-6 rounded-lg bg-bloop-600 flex items-center justify-center text-white">
            <Volume2 className="w-3.5 h-3.5" />
          </div>
          <span className="font-bold text-white font-['Outfit']">Bloop</span>
          <span>— AI Text-to-Speech & Quantum Intelligence</span>
        </div>

        <div className="flex items-center space-x-4 text-xs">
          <Link to="/workspace" className="hover:text-white transition">Workspace</Link>
          <Link to="/quantum" className="hover:text-quantum-300 transition">Quantum Lab</Link>
          <Link to="/history" className="hover:text-white transition">History</Link>
          <Link to="/profile" className="hover:text-white transition">Voices</Link>
        </div>

        <div className="flex items-center space-x-1 text-[11px] text-slate-500">
          <span>Production-style Intermediate Architecture</span>
        </div>
      </div>
    </footer>
  );
};
