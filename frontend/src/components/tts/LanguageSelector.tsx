import React from 'react';
import { Globe } from 'lucide-react';
import { Language } from '../../types';
import { useWorkspaceStore } from '../../stores/workspaceStore';

interface LanguageSelectorProps {
  languages: Language[];
  isLoading?: boolean;
}

export const LanguageSelector: React.FC<LanguageSelectorProps> = ({ languages, isLoading }) => {
  const { languageCode, setLanguageCode } = useWorkspaceStore();

  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center space-x-1.5">
        <Globe className="w-4 h-4 text-bloop-400" />
        <span>Select Language</span>
      </label>

      <div className="relative">
        <select
          value={languageCode}
          onChange={(e) => setLanguageCode(e.target.value)}
          disabled={isLoading}
          className="w-full bg-slate-900/90 text-slate-100 text-sm rounded-xl px-3.5 py-2.5 border border-white/10 focus:outline-none focus:border-bloop-500 appearance-none cursor-pointer pr-10 hover:border-white/20 transition"
        >
          {languages.map((lang) => (
            <option key={lang.code} value={lang.code} className="bg-slate-900 text-white">
              {lang.name} {lang.native_name ? `(${lang.native_name})` : ''} - [{lang.code}]
            </option>
          ))}
        </select>
        <div className="absolute right-3.5 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400 text-xs">
          ▼
        </div>
      </div>
    </div>
  );
};
