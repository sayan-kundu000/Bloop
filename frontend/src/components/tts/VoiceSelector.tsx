import React, { useState, useMemo } from 'react';
import {
  Mic,
  Plus,
  Check,
  Sparkles,
  Search,
  X,
  SlidersHorizontal,
  Globe2,
} from 'lucide-react';
import { Voice } from '../../types';
import { useWorkspaceStore } from '../../stores/workspaceStore';

interface VoiceSelectorProps {
  voices: Voice[];
  currentLanguageCode?: string;
  isLoading?: boolean;
  onAddCustomVoice?: () => void;
  onSelectVoice?: (voice: Voice) => void;
}

export type VoiceCategory = 'All' | 'English' | 'International' | 'Custom';

export function getVoiceCategory(voice: Voice): VoiceCategory {
  if (voice.is_user_configured || voice.provider === 'elevenlabs') {
    return 'Custom';
  }
  const lang = (voice.language_code || '').toLowerCase();
  if (lang.startsWith('en')) {
    return 'English';
  }
  return 'International';
}

export const VoiceSelector: React.FC<VoiceSelectorProps> = ({
  voices,
  currentLanguageCode,
  isLoading,
  onAddCustomVoice,
  onSelectVoice,
}) => {
  const { voiceId, setVoiceId } = useWorkspaceStore();

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<VoiceCategory>('All');
  const [genderFilter, setGenderFilter] = useState<'all' | 'female' | 'male' | 'neutral'>('all');
  const [filterByLanguage, setFilterByLanguage] = useState(false);

  const categories: { label: VoiceCategory; icon: React.ReactNode }[] = [
    { label: 'All', icon: <Sparkles className="w-3.5 h-3.5" /> },
    { label: 'English', icon: <Mic className="w-3.5 h-3.5" /> },
    { label: 'International', icon: <Globe2 className="w-3.5 h-3.5" /> },
    { label: 'Custom', icon: <Plus className="w-3.5 h-3.5" /> },
  ];

  const availableCategories = useMemo(() => {
    const presentCats = new Set(voices.map(getVoiceCategory));
    return categories.filter((c) => c.label === 'All' || presentCats.has(c.label));
  }, [voices]);

  // Filtering pipeline
  const filteredVoices = useMemo(() => {
    return voices.filter((v) => {
      // 1. Language constraint (optional toggle)
      if (filterByLanguage && currentLanguageCode && v.language_code !== currentLanguageCode) {
        return false;
      }

      // 2. Gender filter
      if (genderFilter !== 'all' && v.gender.toLowerCase() !== genderFilter) {
        return false;
      }

      // 3. Category filter
      if (selectedCategory !== 'All') {
        const cat = getVoiceCategory(v);
        if (cat !== selectedCategory) return false;
      }

      // 4. Keyword search
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase().trim();
        const matchesName = v.name.toLowerCase().includes(query);
        const matchesAccent = v.accent?.toLowerCase().includes(query) ?? false;
        const matchesDesc = v.description?.toLowerCase().includes(query) ?? false;
        const matchesId = v.voice_id.toLowerCase().includes(query);
        if (!matchesName && !matchesAccent && !matchesDesc && !matchesId) {
          return false;
        }
      }

      return true;
    });
  }, [voices, filterByLanguage, currentLanguageCode, genderFilter, selectedCategory, searchQuery]);

  const handleSelect = (voice: Voice) => {
    setVoiceId(voice.voice_id);
    if (onSelectVoice) {
      onSelectVoice(voice);
    }
  };

  const getCategoryBadgeColor = (cat: VoiceCategory) => {
    switch (cat) {
      case 'English':
        return 'bg-bloop-500/20 text-bloop-300 border-bloop-500/30';
      case 'International':
        return 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30';
      case 'Custom':
        return 'bg-purple-500/20 text-purple-300 border-purple-500/30';
      default:
        return 'bg-slate-800 text-slate-300 border-white/10';
    }
  };

  return (
    <div className="flex flex-col gap-3.5">
      {/* Selector Header */}
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center space-x-2">
          <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center space-x-1.5">
            <Mic className="w-4 h-4 text-bloop-400" />
            <span>Dynamic Voice Selection</span>
          </label>
          <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-white/5">
            {voices.length} Voices Available
          </span>
        </div>

        {/* Scope Toggle: All vs Filtered by Lang */}
        <div className="flex items-center space-x-1.5 text-xs">
          <button
            type="button"
            onClick={() => setFilterByLanguage(false)}
            className={`px-2.5 py-1 rounded-md text-xs font-medium transition ${
              !filterByLanguage
                ? 'bg-bloop-600/30 text-bloop-300 border border-bloop-500/40'
                : 'text-slate-400 hover:text-white bg-slate-900/60 border border-white/5'
            }`}
          >
            All Voices
          </button>
          {currentLanguageCode && (
            <button
              type="button"
              onClick={() => setFilterByLanguage(true)}
              className={`px-2.5 py-1 rounded-md text-xs font-medium transition ${
                filterByLanguage
                  ? 'bg-bloop-600/30 text-bloop-300 border border-bloop-500/40'
                  : 'text-slate-400 hover:text-white bg-slate-900/60 border border-white/5'
              }`}
            >
              Current Lang ({currentLanguageCode})
            </button>
          )}
        </div>
      </div>

      {/* Search Input Bar */}
      <div className="relative">
        <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search voices by name, language, or accent..."
          className="w-full bg-slate-900/90 text-slate-100 text-xs sm:text-sm rounded-xl pl-10 pr-9 py-2.5 border border-white/10 focus:outline-none focus:border-bloop-500 placeholder:text-slate-500 transition"
        />
        {searchQuery && (
          <button
            type="button"
            onClick={() => setSearchQuery('')}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white transition p-1"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      {/* Category Tabs & Gender Filter */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2.5 pt-0.5">
        {/* Category horizontal scroll bar */}
        <div className="flex items-center space-x-1.5 overflow-x-auto pb-1 max-w-full no-scrollbar">
          {availableCategories.map((cat) => (
            <button
              key={cat.label}
              type="button"
              onClick={() => setSelectedCategory(cat.label)}
              className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-lg text-xs whitespace-nowrap transition border ${
                selectedCategory === cat.label
                  ? 'bg-bloop-600 text-white font-medium border-bloop-500 shadow-sm'
                  : 'bg-slate-900/60 text-slate-400 hover:text-slate-200 border-white/5 hover:border-white/10'
              }`}
            >
              {cat.icon}
              <span>{cat.label}</span>
            </button>
          ))}
        </div>

        {/* Gender Filter Chips */}
        <div className="flex items-center space-x-1 bg-slate-900/90 p-0.5 rounded-lg border border-white/10 text-xs shrink-0 self-end sm:self-auto">
          {(['all', 'male', 'female', 'neutral'] as const).map((g) => (
            <button
              key={g}
              type="button"
              onClick={() => setGenderFilter(g)}
              className={`px-2 py-0.5 rounded capitalize transition text-[11px] ${
                genderFilter === g
                  ? 'bg-bloop-600 text-white font-medium'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {g}
            </button>
          ))}
        </div>
      </div>

      {/* Voice Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 animate-pulse">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="h-24 bg-slate-800/40 rounded-xl border border-white/5" />
          ))}
        </div>
      ) : filteredVoices.length === 0 ? (
        <div className="p-8 text-center rounded-xl bg-slate-900/60 border border-white/10 text-slate-400 text-sm flex flex-col items-center justify-center gap-2">
          <SlidersHorizontal className="w-6 h-6 text-slate-500" />
          <p>No voices match the current filters.</p>
          {(searchQuery || selectedCategory !== 'All' || genderFilter !== 'all') && (
            <button
              type="button"
              onClick={() => {
                setSearchQuery('');
                setSelectedCategory('All');
                setGenderFilter('all');
                setFilterByLanguage(false);
              }}
              className="text-xs text-bloop-400 hover:underline"
            >
              Clear filters
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 max-h-[380px] overflow-y-auto pr-1">
          {filteredVoices.map((voice) => {
            const isSelected = voice.voice_id === voiceId;
            const category = getVoiceCategory(voice);
            const badgeColor = getCategoryBadgeColor(category);

            return (
              <button
                key={voice.voice_id}
                type="button"
                onClick={() => handleSelect(voice)}
                className={`flex flex-col p-3 rounded-xl text-left transition relative border group ${
                  isSelected
                    ? 'bg-bloop-600/20 border-bloop-500 shadow-lg shadow-bloop-500/15 ring-1 ring-bloop-500/50'
                    : 'bg-slate-900/75 border-white/10 hover:border-white/20 hover:bg-slate-800/60'
                }`}
              >
                {/* Title & Selection */}
                <div className="flex items-start justify-between w-full gap-2">
                  <div className="flex items-center space-x-2 min-w-0">
                    <span className="font-semibold text-sm text-white truncate group-hover:text-bloop-300 transition">
                      {voice.name}
                    </span>
                    {voice.is_user_configured && (
                      <span className="text-[9px] px-1.5 py-0.2 rounded bg-quantum-500/20 text-quantum-300 border border-quantum-500/30 shrink-0">
                        Injected
                      </span>
                    )}
                  </div>
                  {isSelected && (
                    <div className="w-5 h-5 rounded-full bg-bloop-500 flex items-center justify-center text-white shrink-0">
                      <Check className="w-3 h-3" />
                    </div>
                  )}
                </div>

                {/* Badges & Meta */}
                <div className="flex flex-wrap items-center gap-1.5 mt-2 text-xs">
                  <span className={`text-[10px] px-1.5 py-0.5 rounded border ${badgeColor}`}>
                    {category}
                  </span>
                  <span className="capitalize text-[10px] px-1.5 py-0.5 rounded bg-slate-800 border border-white/5 text-slate-300">
                    {voice.gender}
                  </span>
                  {voice.accent && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 border border-white/5 text-slate-400">
                      {voice.accent}
                    </span>
                  )}
                  <span className="text-[10px] text-slate-500 font-mono">
                    {voice.language_code}
                  </span>
                </div>

                {/* Description */}
                {voice.description && (
                  <p className="text-[11px] text-slate-400/90 mt-1.5 line-clamp-2 leading-relaxed">
                    {voice.description}
                  </p>
                )}
              </button>
            );
          })}
        </div>
      )}

      {/* Dynamic Voice Injection Notice & Footer Action */}
      <div className="flex items-center justify-between text-xs text-slate-400 pt-1.5 border-t border-white/5">
        <span className="flex items-center space-x-1.5">
          <Sparkles className="w-3.5 h-3.5 text-quantum-400" />
          <span>
            Showing <strong className="text-slate-200">{filteredVoices.length}</strong> of{' '}
            {voices.length} dynamic voices
          </span>
        </span>
        {onAddCustomVoice && (
          <button
            type="button"
            onClick={onAddCustomVoice}
            className="flex items-center space-x-1 text-bloop-400 hover:text-bloop-300 font-medium transition"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Inject Custom Voice ID</span>
          </button>
        )}
      </div>
    </div>
  );
};
