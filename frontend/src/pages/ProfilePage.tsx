import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  User as UserIcon,
  Key,
  Mic,
  Plus,
  CheckCircle2,
  Shield,
  Edit2,
  Save,
  X,
  Sliders,
  Moon,
  Sun,
  Laptop,
  Volume2,
  Globe,
  Loader2,
  AlertCircle,
} from 'lucide-react';
import { useAuthStore } from '../stores/authStore';
import { voiceApi, userApi } from '../api/client';
import { AddVoiceModal } from '../components/tts/AddVoiceModal';
import { UpdateProfilePayload, UpdatePreferencesPayload } from '../types';

export const ProfilePage: React.FC = () => {
  const queryClient = useQueryClient();
  const { user } = useAuthStore();
  const [isVoiceModalOpen, setIsVoiceModalOpen] = useState(false);

  // Profile Edit State
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [fullNameInput, setFullNameInput] = useState(user?.full_name || '');
  const [profileSuccessMsg, setProfileSuccessMsg] = useState<string | null>(null);

  // Preferences Edit State
  const [prefSuccessMsg, setPrefSuccessMsg] = useState<string | null>(null);

  // Fetch full user profile & preferences from API
  const { data: userProfile, isLoading: isProfileLoading } = useQuery({
    queryKey: ['user-profile'],
    queryFn: () => userApi.getProfile(),
  });

  const { data: preferences, isLoading: isPrefsLoading } = useQuery({
    queryKey: ['user-preferences'],
    queryFn: () => userApi.getPreferences(),
  });

  // Fetch all voices to display custom injected voices
  const { data: voices = [] } = useQuery({
    queryKey: ['voices'],
    queryFn: () => voiceApi.getVoices(),
  });

  const { data: languages = [] } = useQuery({
    queryKey: ['languages'],
    queryFn: voiceApi.getLanguages,
  });

  // Profile Update Mutation
  const updateProfileMutation = useMutation({
    mutationFn: (payload: UpdateProfilePayload) => userApi.updateProfile(payload),
    onSuccess: (updated) => {
      queryClient.invalidateQueries({ queryKey: ['user-profile'] });
      queryClient.invalidateQueries({ queryKey: ['currentUser'] });
      setIsEditingProfile(false);
      setProfileSuccessMsg('Profile updated successfully.');
      setTimeout(() => setProfileSuccessMsg(null), 4000);
    },
  });

  // Preferences Update Mutation
  const updatePrefsMutation = useMutation({
    mutationFn: (payload: UpdatePreferencesPayload) => userApi.updatePreferences(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-preferences'] });
      queryClient.invalidateQueries({ queryKey: ['user-profile'] });
      setPrefSuccessMsg('Preferences saved successfully.');
      setTimeout(() => setPrefSuccessMsg(null), 4000);
    },
  });

  const handleProfileSave = (e: React.FormEvent) => {
    e.preventDefault();
    updateProfileMutation.mutate({ full_name: fullNameInput.trim() });
  };

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

  const userInjectedVoices = voices.filter((v) => v.is_user_configured);

  const displayUser = userProfile || user;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center space-x-3">
          <UserIcon className="w-8 h-8 text-bloop-400" />
          <span>Account & <span className="gradient-text-bloop">Preferences</span></span>
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Manage your personal account information, configure TTS preferences, and manage dynamic voice registrations.
        </p>
      </div>

      <div className="flex flex-col gap-8">
        {/* User Account Details */}
        <div className="glass-panel rounded-2xl p-6 border border-white/10 shadow-xl">
          <div className="flex items-center justify-between border-b border-white/10 pb-4 mb-5">
            <div className="flex items-center space-x-3">
              <Shield className="w-5 h-5 text-bloop-400" />
              <h3 className="font-bold text-white text-base">User Profile</h3>
            </div>

            {!isEditingProfile && (
              <button
                onClick={() => {
                  setFullNameInput(displayUser?.full_name || '');
                  setIsEditingProfile(true);
                }}
                className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-white/10 text-xs font-medium transition"
              >
                <Edit2 className="w-3.5 h-3.5" />
                <span>Edit Profile</span>
              </button>
            )}
          </div>

          {profileSuccessMsg && (
            <div className="mb-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>{profileSuccessMsg}</span>
            </div>
          )}

          {updateProfileMutation.isError && (
            <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{updateProfileMutation.error.message}</span>
            </div>
          )}

          {isEditingProfile ? (
            <form onSubmit={handleProfileSave} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Display Full Name (Max 100 characters)
                </label>
                <input
                  type="text"
                  maxLength={100}
                  value={fullNameInput}
                  onChange={(e) => setFullNameInput(e.target.value)}
                  placeholder="Enter display name"
                  className="w-full bg-slate-900 border border-white/10 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-bloop-500 transition"
                />
              </div>

              <div className="flex items-center space-x-2 pt-1">
                <button
                  type="submit"
                  disabled={updateProfileMutation.isPending}
                  className="flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-bloop-600 hover:bg-bloop-500 text-white font-medium text-xs shadow-md transition disabled:opacity-50"
                >
                  {updateProfileMutation.isPending ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <Save className="w-3.5 h-3.5" />
                  )}
                  <span>Save Changes</span>
                </button>
                <button
                  type="button"
                  onClick={() => setIsEditingProfile(false)}
                  className="flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium transition"
                >
                  <X className="w-3.5 h-3.5" />
                  <span>Cancel</span>
                </button>
              </div>
            </form>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
              <div className="p-3.5 rounded-xl bg-slate-900/70 border border-white/5">
                <span className="text-xs text-slate-400 block mb-1">Email Address (Immutable)</span>
                <span className="font-semibold text-white">{displayUser?.email || 'Guest / Not signed in'}</span>
              </div>
              <div className="p-3.5 rounded-xl bg-slate-900/70 border border-white/5">
                <span className="text-xs text-slate-400 block mb-1">Full Name</span>
                <span className="font-semibold text-white">{displayUser?.full_name || 'Not configured'}</span>
              </div>
              <div className="p-3.5 rounded-xl bg-slate-900/70 border border-white/5">
                <span className="text-xs text-slate-400 block mb-1">Account Role</span>
                <span className="font-mono text-xs text-bloop-300">
                  {displayUser?.is_superuser ? 'Superuser' : 'Standard User'}
                </span>
              </div>
              <div className="p-3.5 rounded-xl bg-slate-900/70 border border-white/5">
                <span className="text-xs text-slate-400 block mb-1">Status</span>
                <span className="inline-flex items-center space-x-1 text-emerald-400 font-medium">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Active</span>
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Application Preferences */}
        <div className="glass-panel rounded-2xl p-6 border border-white/10 shadow-xl">
          <div className="flex items-center justify-between border-b border-white/10 pb-4 mb-5">
            <div className="flex items-center space-x-3">
              <Sliders className="w-5 h-5 text-bloop-400" />
              <div>
                <h3 className="font-bold text-white text-base">User Preferences</h3>
                <p className="text-xs text-slate-400">Configure playback speed, theme, and language defaults</p>
              </div>
            </div>

            {updatePrefsMutation.isPending && (
              <span className="flex items-center space-x-1 text-xs text-bloop-400 animate-pulse">
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Saving...</span>
              </span>
            )}
          </div>

          {prefSuccessMsg && (
            <div className="mb-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>{prefSuccessMsg}</span>
            </div>
          )}

          {isPrefsLoading ? (
            <div className="h-32 rounded-xl bg-slate-900/50 animate-pulse" />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {/* Theme Preference */}
              <div className="p-4 rounded-xl bg-slate-900/70 border border-white/5">
                <span className="text-xs font-semibold text-white block mb-2">Interface Theme</span>
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
                        className={`flex items-center space-x-1.5 px-3 py-2 rounded-xl text-xs font-medium transition ${
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

              {/* Default Language Preference */}
              <div className="p-4 rounded-xl bg-slate-900/70 border border-white/5">
                <span className="text-xs font-semibold text-white block mb-2 flex items-center space-x-1.5">
                  <Globe className="w-3.5 h-3.5 text-bloop-400" />
                  <span>Default Language</span>
                </span>
                <select
                  value={preferences?.default_language_code || ''}
                  onChange={(e) => handleLanguageChange(e.target.value)}
                  className="w-full bg-slate-800 text-xs text-white rounded-xl px-3 py-2 border border-white/10 focus:outline-none focus:border-bloop-500"
                >
                  <option value="">No default language</option>
                  {languages.map((l) => (
                    <option key={l.code} value={l.code}>
                      {l.name} ({l.code})
                    </option>
                  ))}
                </select>
              </div>

              {/* Playback Speed Preference */}
              <div className="p-4 rounded-xl bg-slate-900/70 border border-white/5">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold text-white">Default Audio Playback Speed</span>
                  <span className="font-mono text-xs text-bloop-300">
                    {preferences?.audio_speed ? `${preferences.audio_speed}x` : '1.0x'}
                  </span>
                </div>
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
                  <span>1.0x (Normal)</span>
                  <span>2.0x</span>
                </div>
              </div>

              {/* Auto-Play Toggle */}
              <div className="p-4 rounded-xl bg-slate-900/70 border border-white/5 flex items-center justify-between">
                <div>
                  <span className="text-xs font-semibold text-white block mb-0.5">Auto-Play Synthesized Audio</span>
                  <span className="text-[11px] text-slate-400 block">
                    Automatically trigger audio playback upon speech generation completion
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
          )}
        </div>

        {/* ElevenLabs Provider Status & Guidance */}
        <div className="glass-panel rounded-2xl p-6 border border-white/10 shadow-xl">
          <div className="flex items-center space-x-3 border-b border-white/10 pb-4 mb-4">
            <Key className="w-5 h-5 text-quantum-400" />
            <h3 className="font-bold text-white text-base">ElevenLabs TTS Provider Integration</h3>
          </div>

          <div className="flex flex-col gap-3 text-sm">
            <div className="p-4 rounded-xl bg-slate-950/70 border border-white/10 flex items-start space-x-3">
              <div className="p-2 rounded-lg bg-bloop-600/20 text-bloop-400 shrink-0 mt-0.5">
                <Key className="w-4 h-4" />
              </div>
              <div className="text-xs leading-relaxed text-slate-300">
                <p className="font-semibold text-white text-sm mb-1">Secure Backend-Only API Key Isolation</p>
                <p>
                  In accordance with Bloop's security architecture, the ElevenLabs API Key is never exposed to the frontend browser.
                  To connect your production ElevenLabs account, simply set the following in your backend environment:
                </p>
                <code className="block mt-2 p-2.5 rounded bg-slate-900 text-bloop-300 font-mono text-xs border border-white/5">
                  ELEVENLABS_API_KEY=your_actual_elevenlabs_api_key_here
                </code>
                <p className="mt-2 text-slate-400">
                  When this key is absent, Bloop automatically runs in high-fidelity simulation mode with zero crashes.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Dynamic Voice Registry Management */}
        <div className="glass-panel rounded-2xl p-6 border border-white/10 shadow-xl">
          <div className="flex items-center justify-between border-b border-white/10 pb-4 mb-5">
            <div className="flex items-center space-x-3">
              <Mic className="w-5 h-5 text-bloop-400" />
              <div>
                <h3 className="font-bold text-white text-base">User-Injected Voices</h3>
                <p className="text-xs text-slate-400">Voices injected dynamically via UI or voices_config.json</p>
              </div>
            </div>

            <button
              onClick={() => setIsVoiceModalOpen(true)}
              className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-bloop-600 hover:bg-bloop-500 text-white font-medium text-xs shadow-md transition"
            >
              <Plus className="w-4 h-4" />
              <span>Inject Voice ID</span>
            </button>
          </div>

          {userInjectedVoices.length === 0 ? (
            <div className="p-6 rounded-xl bg-slate-900/50 border border-white/10 text-center text-slate-400 text-sm">
              <p className="font-medium text-slate-300">No user-injected voices yet.</p>
              <p className="text-xs text-slate-500 mt-1">
                Click "Inject Voice ID" above to add your custom ElevenLabs voices dynamically without touching source code.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {userInjectedVoices.map((v) => (
                <div key={v.voice_id} className="p-3.5 rounded-xl bg-slate-900/80 border border-white/10 text-xs">
                  <div className="flex items-center justify-between font-semibold text-white mb-1">
                    <span>{v.name}</span>
                    <span className="font-mono text-[10px] text-quantum-300 bg-quantum-500/20 px-1.5 py-0.5 rounded">
                      {v.provider}
                    </span>
                  </div>
                  <p className="font-mono text-slate-400 text-[11px] truncate mb-2">ID: {v.voice_id}</p>
                  <div className="flex items-center space-x-2 text-slate-500">
                    <span className="capitalize">{v.gender}</span>
                    <span>•</span>
                    <span>{v.language_code}</span>
                    {v.accent && (
                      <>
                        <span>•</span>
                        <span>{v.accent}</span>
                      </>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <AddVoiceModal
        isOpen={isVoiceModalOpen}
        onClose={() => setIsVoiceModalOpen(false)}
        onSuccess={() => {
          queryClient.invalidateQueries({ queryKey: ['voices'] });
        }}
        languages={languages}
      />
    </div>
  );
};
