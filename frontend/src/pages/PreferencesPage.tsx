import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Sliders,
  Moon,
  Sun,
  Laptop,
  Globe,
  Loader2,
  CheckCircle2,
  AlertCircle,
  Volume2,
} from 'lucide-react';
import { userApi, voiceApi } from '../api/client';
import { UpdatePreferencesPayload } from '../types';

export const PreferencesPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const { data: preferences, isLoading: isPrefsLoading, isError, error } = useQuery({
    queryKey: ['user-preferences'],
    queryFn: () => userApi.getPreferences(),
  });

  const { data: languages = [] } = useQuery({
    queryKey: ['languages'],
    queryFn: voiceApi.getLanguages,
  });

  const updatePrefsMutation = useMutation({
    mutationFn: (payload: UpdatePreferencesPayload) => userApi.updatePreferences(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-preferences'] });
      queryClient.invalidateQueries({ queryKey: ['user-profile'] });
      setSuccessMsg('Preferences updated successfully.');
      setTimeout(() => setSuccessMsg(null), 4000);
    },
  });

  const handleThemeChange = (newTheme: 'dark' | 'light' | 'system') => {
    updatePrefsMutation.mutate({ theme: newTheme });
  };

  const handleSpeedChange = (newSpeed: number) => {
    updatePrefsMutation.mutate({ audio_speed: newSpeed });
  };

  const handleAutoPlayToggle = () => {
    if (preferences) {
      updatePrefsMutation.mutate({ auto_play: !preferences.auto_play });
    }
  };

  const handleLanguageChange = (langCode: string) => {
    updatePrefsMutation.mutate({ default_language_code: langCode || null });
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center space-x-3">
          <Sliders className="w-8 h-8 text-bloop-400" />
          <span>Application <span className="gradient-text-bloop">Preferences</span></span>
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Customize your speech generation parameters, interface theme, and default audio settings.
        </p>
      </div>

      {successMsg && (
        <div className="mb-6 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {isError && (
        <div className="mb-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{(error as Error)?.message || 'Failed to load user preferences.'}</span>
        </div>
      )}

      {isPrefsLoading ? (
        <div className="glass-panel rounded-2xl p-12 text-center border border-white/10 flex flex-col items-center justify-center gap-3">
          <Loader2 className="w-8 h-8 text-bloop-400 animate-spin" />
          <p className="text-sm text-slate-400">Loading user preferences...</p>
        </div>
      ) : (
        <div className="glass-panel rounded-2xl p-6 border border-white/10 shadow-xl space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Theme */}
            <div className="p-4 rounded-xl bg-slate-900/70 border border-white/5">
              <span className="text-xs font-semibold text-white block mb-2">Interface Theme</span>
              <p className="text-xs text-slate-400 mb-3">Select your preferred color scheme across the application.</p>
              <div className="flex items-center space-x-2">
                {[
                  { id: 'dark', label: 'Dark', icon: Moon },
                  { id: 'light', label: 'Light', icon: Sun },
                  { id: 'system', label: 'System', icon: Laptop },
                ].map((t) => {
                  const Icon = t.icon;
                  const isSelected = (preferences?.theme || 'dark') === t.id;
                  return (
                    <button
                      key={t.id}
                      type="button"
                      onClick={() => handleThemeChange(t.id as any)}
                      className={`flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs font-medium transition ${
                        isSelected
                          ? 'bg-bloop-600 text-white shadow-md'
                          : 'bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-white'
                      }`}
                    >
                      <Icon className="w-3.5 h-3.5" />
                      <span>{t.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Default Language */}
            <div className="p-4 rounded-xl bg-slate-900/70 border border-white/5">
              <span className="text-xs font-semibold text-white block mb-2 flex items-center space-x-1.5">
                <Globe className="w-3.5 h-3.5 text-bloop-400" />
                <span>Default Language</span>
              </span>
              <p className="text-xs text-slate-400 mb-3">Pre-selected language for new speech synthesis sessions.</p>
              <select
                value={preferences?.default_language_code || ''}
                onChange={(e) => handleLanguageChange(e.target.value)}
                className="w-full bg-slate-800 text-xs text-white rounded-xl px-3.5 py-2.5 border border-white/10 focus:outline-none focus:border-bloop-500 cursor-pointer"
              >
                <option value="">No default language</option>
                {languages.map((l) => (
                  <option key={l.code} value={l.code}>
                    {l.name} ({l.code})
                  </option>
                ))}
              </select>
            </div>

            {/* Audio Speed */}
            <div className="p-4 rounded-xl bg-slate-900/70 border border-white/5">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-white">Default Playback Speed</span>
                <span className="font-mono text-xs text-bloop-300">
                  {preferences?.audio_speed ? `${preferences.audio_speed}x` : '1.0x'}
                </span>
              </div>
              <p className="text-xs text-slate-400 mb-3">Speed multiplier applied to audio playback elements.</p>
              <input
                type="range"
                min="0.5"
                max="2.0"
                step="0.1"
                value={preferences?.audio_speed || 1.0}
                onChange={(e) => handleSpeedChange(parseFloat(e.target.value))}
                className="w-full accent-bloop-500 cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-500 mt-1 font-mono">
                <span>0.5x</span>
                <span>1.0x</span>
                <span>2.0x</span>
              </div>
            </div>

            {/* Auto Play */}
            <div className="p-4 rounded-xl bg-slate-900/70 border border-white/5 flex items-center justify-between">
              <div>
                <span className="text-xs font-semibold text-white block mb-0.5">Auto-Play Audio</span>
                <span className="text-[11px] text-slate-400 block">
                  Instantly play generated speech upon completion.
                </span>
              </div>
              <button
                type="button"
                onClick={handleAutoPlayToggle}
                className={`w-12 h-6 flex items-center rounded-full p-1 transition duration-300 cursor-pointer ${
                  preferences?.auto_play ? 'bg-bloop-600' : 'bg-slate-700'
                }`}
              >
                <div
                  className={`bg-white w-4 h-4 rounded-full shadow-md transform transition duration-300 ${
                    preferences?.auto_play ? 'translate-x-6' : 'translate-x-0'
                  }`}
                />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
