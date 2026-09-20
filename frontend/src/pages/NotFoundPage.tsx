import React from 'react';
import { Link } from 'react-router-dom';
import { Volume2, ArrowLeft, Home, Compass } from 'lucide-react';
import { Button } from '../components/ui';

export const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-[70vh] flex items-center justify-center px-4 py-12">
      <div className="max-w-md w-full glass-panel border border-white/10 rounded-2xl p-8 text-center shadow-2xl relative overflow-hidden">
        {/* Background ambient glow */}
        <div className="absolute -top-16 -right-16 w-36 h-36 bg-bloop-500/15 rounded-full blur-2xl pointer-events-none" />
        <div className="absolute -bottom-16 -left-16 w-36 h-36 bg-quantum-500/15 rounded-full blur-2xl pointer-events-none" />

        {/* 404 Badge */}
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700 text-xs font-mono text-bloop-300 mb-6">
          <Compass className="w-3.5 h-3.5 text-bloop-400" />
          <span>HTTP 404 — NOT FOUND</span>
        </div>

        <h1 className="text-3xl sm:text-4xl font-extrabold text-white font-['Outfit'] tracking-tight mb-3">
          Page Not Found
        </h1>

        <p className="text-sm text-slate-400 mb-8 leading-relaxed">
          The screen or resource you are looking for does not exist, has been moved,
          or is temporarily unreachable.
        </p>

        {/* Primary Action Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
          <Link to="/workspace" className="w-full sm:w-auto">
            <Button variant="primary" size="md" className="w-full">
              <Volume2 className="w-4 h-4 mr-2" />
              Go to Workspace
            </Button>
          </Link>
          <Link to="/dashboard" className="w-full sm:w-auto">
            <Button variant="secondary" size="md" className="w-full">
              <Home className="w-4 h-4 mr-2" />
              Dashboard
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
};
