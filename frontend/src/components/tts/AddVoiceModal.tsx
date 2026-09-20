import React, { useState } from 'react';
import { X, Mic, Plus } from 'lucide-react';
import { voiceApi } from '../../api/client';
import { Language } from '../../types';

interface AddVoiceModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  languages: Language[];
}

export const AddVoiceModal: React.FC<AddVoiceModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  languages,
}) => {
  const [voiceId, setVoiceId] = useState('');
  const [name, setName] = useState('');
  const [languageCode, setLanguageCode] = useState('en-US');
  const [gender, setGender] = useState<'female' | 'male' | 'neutral'>('female');
  const [accent, setAccent] = useState('American');
  const [description, setDescription] = useState('');
  const [provider, setProvider] = useState('elevenlabs');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!voiceId.trim() || !name.trim()) {
      setError('Voice ID and Name are required.');
      return;
    }
    setError(null);
    setIsSubmitting(true);
    try {
      await voiceApi.registerVoice({
        voice_id: voiceId.trim(),
        name: name.trim(),
        language_code: languageCode,
        gender,
        accent: accent.trim() || undefined,
        description: description.trim() || undefined,
        provider,
        is_active: true,
      });
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to register voice.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <div className="glass-panel w-full max-w-md rounded-2xl p-6 border border-white/10 shadow-2xl relative">
        <div className="flex items-center justify-between border-b border-white/10 pb-4 mb-4">
          <div className="flex items-center space-x-2">
            <Mic className="w-5 h-5 text-bloop-400" />
            <h3 className="text-lg font-bold text-white font-['Outfit']">Inject Custom Voice</h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white p-1">
            <X className="w-5 h-5" />
          </button>
        </div>

        {error && (
          <div className="p-3 mb-4 rounded-lg bg-rose-500/10 border border-rose-500/30 text-xs text-rose-400">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex flex-col gap-3.5 text-sm">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              ElevenLabs Voice ID <span className="text-rose-400">*</span>
            </label>
            <input
              type="text"
              value={voiceId}
              onChange={(e) => setVoiceId(e.target.value)}
              placeholder="e.g. 21m00Tcm4TlvDq8ikWAM"
              className="w-full bg-slate-900 rounded-lg p-2.5 border border-white/10 text-white focus:outline-none focus:border-bloop-500 font-mono text-xs"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Voice Display Name <span className="text-rose-400">*</span>
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Studio Rachel"
              className="w-full bg-slate-900 rounded-lg p-2.5 border border-white/10 text-white focus:outline-none focus:border-bloop-500 text-sm"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Language</label>
              <select
                value={languageCode}
                onChange={(e) => setLanguageCode(e.target.value)}
                className="w-full bg-slate-900 rounded-lg p-2.5 border border-white/10 text-white focus:outline-none focus:border-bloop-500 text-xs"
              >
                {languages.map((l) => (
                  <option key={l.code} value={l.code}>
                    {l.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Gender</label>
              <select
                value={gender}
                onChange={(e) => setGender(e.target.value as any)}
                className="w-full bg-slate-900 rounded-lg p-2.5 border border-white/10 text-white focus:outline-none focus:border-bloop-500 text-xs"
              >
                <option value="female">Female</option>
                <option value="male">Male</option>
                <option value="neutral">Neutral</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Accent / Tone</label>
            <input
              type="text"
              value={accent}
              onChange={(e) => setAccent(e.target.value)}
              placeholder="e.g. American, British, Expressive"
              className="w-full bg-slate-900 rounded-lg p-2.5 border border-white/10 text-white focus:outline-none focus:border-bloop-500 text-xs"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Provider</label>
            <select
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
              className="w-full bg-slate-900 rounded-lg p-2.5 border border-white/10 text-white focus:outline-none focus:border-bloop-500 text-xs"
            >
              <option value="elevenlabs">ElevenLabs</option>
              <option value="dynamic">Dynamic Slot</option>
            </select>
          </div>

          <div className="flex items-center justify-end space-x-3 pt-4 border-t border-white/10 mt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-5 py-2 rounded-lg bg-bloop-600 hover:bg-bloop-500 text-white font-medium shadow-md shadow-bloop-600/30 transition flex items-center space-x-1.5"
            >
              {isSubmitting ? (
                <span>Registering...</span>
              ) : (
                <>
                  <Plus className="w-4 h-4" />
                  <span>Register Voice</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
