import React, { useState, useMemo } from 'react';
import {
  Sparkles,
  Search,
  X,
  Check,
  RotateCcw,
  Sliders,
  ChevronDown,
  ChevronUp,
  Smile,
  Volume2,
} from 'lucide-react';
import { EMOTIONS, EMOTION_CATEGORIES, EmotionCategory, EmotionItem } from '../../data/emotions';
import { useWorkspaceStore } from '../../stores/workspaceStore';

interface EmotionBoxProps {
  onSelectEmotion?: (emotion: EmotionItem) => void;
}

export const EmotionBox: React.FC<EmotionBoxProps> = ({ onSelectEmotion }) => {
  const { emotion: activeEmotionName, emotionId: activeEmotionId, setEmotion } = useWorkspaceStore();

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<EmotionCategory>('All');
  const [isExpanded, setIsExpanded] = useState(false);

  // Find the currently active emotion object
  const currentEmotion = useMemo(() => {
    return (
      EMOTIONS.find((e) => e.id === activeEmotionId) ||
      EMOTIONS.find((e) => e.name.toLowerCase() === activeEmotionName.toLowerCase()) ||
      EMOTIONS[0]
    );
  }, [activeEmotionId, activeEmotionName]);

  // Filter emotions based on search query and category
  const filteredEmotions = useMemo(() => {
    return EMOTIONS.filter((item) => {
      // Category filter
      if (selectedCategory !== 'All' && item.category !== selectedCategory) {
        return false;
      }

      // Search filter
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase().trim();
        const matchesName = item.name.toLowerCase().includes(q);
        const matchesDesc = item.description.toLowerCase().includes(q);
        const matchesId = item.id.toString() === q || `#${item.id}` === q;
        const matchesCat = item.category.toLowerCase().includes(q);
        if (!matchesName && !matchesDesc && !matchesId && !matchesCat) {
          return false;
        }
      }

      return true;
    });
  }, [selectedCategory, searchQuery]);

  const handleSelect = (item: EmotionItem) => {
    setEmotion(item.name, item.id);
    if (onSelectEmotion) {
      onSelectEmotion(item);
    }
  };

  const handleReset = () => {
    const neutral = EMOTIONS[0];
    setEmotion(neutral.name, neutral.id);
    if (onSelectEmotion) {
      onSelectEmotion(neutral);
    }
  };

  // Helper for category badge styling
  const getCategoryBadgeClass = (category: EmotionCategory) => {
    switch (category) {
      case 'Positive & Joy':
        return 'bg-amber-500/15 text-amber-300 border-amber-500/30';
      case 'Warm & Romantic':
        return 'bg-rose-500/15 text-rose-300 border-rose-500/30';
      case 'Calm & Soothing':
        return 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30';
      case 'Confident & Resolute':
        return 'bg-blue-500/15 text-blue-300 border-blue-500/30';
      case 'Intense & Urgent':
        return 'bg-red-500/15 text-red-300 border-red-500/30';
      case 'Sad & Vulnerable':
        return 'bg-indigo-500/15 text-indigo-300 border-indigo-500/30';
      case 'Anxious & Guarded':
        return 'bg-orange-500/15 text-orange-300 border-orange-500/30';
      case 'Wonder & Mystery':
        return 'bg-purple-500/15 text-purple-300 border-purple-500/30';
      case 'Expressive & Nuanced':
        return 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30';
      default:
        return 'bg-slate-800 text-slate-300 border-white/10';
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-5 border border-white/10 flex flex-col gap-4 shadow-xl relative overflow-hidden transition-all duration-300">
      {/* Subtle background glow */}
      <div className="absolute top-0 right-0 w-44 h-44 bg-gradient-to-br from-bloop-500/10 via-purple-500/5 to-transparent rounded-full blur-2xl pointer-events-none" />

      {/* Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-white/10 pb-3 relative z-10">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-bloop-500/30 to-purple-500/30 border border-bloop-500/40 flex items-center justify-center text-bloop-300 shadow-sm">
            <Smile className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-base font-bold text-white tracking-tight">Emotion Box</h2>
              <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-bloop-500/20 text-bloop-300 border border-bloop-500/40 font-semibold">
                77 Expressive Emotions
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Calibrate vocal tone, affective delivery, and emotional inflection
            </p>
          </div>
        </div>

        {/* Reset to Neutral button */}
        {currentEmotion.id !== 1 && (
          <button
            onClick={handleReset}
            className="flex items-center space-x-1.5 px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white border border-white/10 transition shadow-sm"
            title="Reset to Neutral"
          >
            <RotateCcw className="w-3 h-3 text-slate-400" />
            <span>Reset to Neutral</span>
          </button>
        )}
      </div>

      {/* Active Emotion Spotlight Banner */}
      <div className="p-3.5 rounded-xl bg-gradient-to-r from-slate-900/90 via-slate-950/80 to-slate-900/90 border border-white/15 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-inner relative z-10">
        <div className="flex items-start sm:items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-bloop-500 to-quantum-600 flex items-center justify-center font-mono font-black text-sm text-white shadow-md shadow-bloop-500/30 shrink-0">
            {currentEmotion.id}
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-base font-bold text-white tracking-wide">
                {currentEmotion.name}
              </span>
              <span
                className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full border ${getCategoryBadgeClass(
                  currentEmotion.category
                )}`}
              >
                {currentEmotion.category}
              </span>
            </div>
            <p className="text-xs text-slate-300 mt-0.5 font-medium leading-relaxed">
              {currentEmotion.description}
            </p>
          </div>
        </div>

        {/* Dynamic Acoustic Calibration Pills */}
        <div className="flex items-center space-x-2 text-[11px] font-mono shrink-0 self-end sm:self-center">
          <div className="px-2 py-1 rounded-md bg-slate-900 border border-white/10 text-slate-300 flex items-center space-x-1">
            <Sliders className="w-3 h-3 text-bloop-400" />
            <span className="text-slate-400">Pitch:</span>
            <span className={currentEmotion.pitchOffsetHz && currentEmotion.pitchOffsetHz > 0 ? 'text-emerald-400 font-bold' : currentEmotion.pitchOffsetHz && currentEmotion.pitchOffsetHz < 0 ? 'text-amber-400 font-bold' : 'text-slate-300'}>
              {currentEmotion.pitchOffsetHz && currentEmotion.pitchOffsetHz > 0 ? `+${currentEmotion.pitchOffsetHz}Hz` : `${currentEmotion.pitchOffsetHz || 0}Hz`}
            </span>
          </div>

          <div className="px-2 py-1 rounded-md bg-slate-900 border border-white/10 text-slate-300 flex items-center space-x-1">
            <Volume2 className="w-3 h-3 text-quantum-400" />
            <span className="text-slate-400">Rate:</span>
            <span className={currentEmotion.rateOffsetPct && currentEmotion.rateOffsetPct > 0 ? 'text-emerald-400 font-bold' : currentEmotion.rateOffsetPct && currentEmotion.rateOffsetPct < 0 ? 'text-amber-400 font-bold' : 'text-slate-300'}>
              {currentEmotion.rateOffsetPct && currentEmotion.rateOffsetPct > 0 ? `+${currentEmotion.rateOffsetPct}%` : `${currentEmotion.rateOffsetPct || 0}%`}
            </span>
          </div>
        </div>
      </div>

      {/* Search and Category Filter Bar */}
      <div className="flex flex-col gap-2.5 relative z-10">
        {/* Search input */}
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search 77 emotions by name, #ID, delivery style (e.g. cheerful, whisper, angry)..."
            className="w-full bg-slate-950/70 text-slate-100 placeholder-slate-500 text-xs rounded-xl pl-9 pr-9 py-2.5 border border-white/10 focus:outline-none focus:border-bloop-500 transition"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Category Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-thin scrollbar-thumb-slate-800 text-xs">
          {EMOTION_CATEGORIES.map((cat) => {
            const count =
              cat === 'All'
                ? EMOTIONS.length
                : EMOTIONS.filter((e) => e.category === cat).length;
            const isSelected = selectedCategory === cat;

            return (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`whitespace-nowrap px-2.5 py-1 rounded-lg font-medium text-xs transition flex items-center space-x-1.5 ${
                  isSelected
                    ? 'bg-bloop-600 text-white shadow-md shadow-bloop-600/30'
                    : 'bg-slate-900/80 hover:bg-slate-800 text-slate-400 hover:text-slate-200 border border-white/5'
                }`}
              >
                <span>{cat}</span>
                <span
                  className={`text-[10px] px-1.5 py-0.2 rounded-full font-mono ${
                    isSelected ? 'bg-white/20 text-white' : 'bg-slate-800 text-slate-500'
                  }`}
                >
                  {count}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Emotions Selection Grid / List */}
      <div
        className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 overflow-y-auto pr-1 transition-all duration-300 scrollbar-thin scrollbar-thumb-slate-800 ${
          isExpanded ? 'max-h-[460px]' : 'max-h-[260px]'
        }`}
      >
        {filteredEmotions.length === 0 ? (
          <div className="col-span-full py-8 text-center text-slate-500 text-xs">
            No emotions found matching "{searchQuery}".
          </div>
        ) : (
          filteredEmotions.map((item) => {
            const isSelected = currentEmotion.id === item.id;

            return (
              <button
                key={item.id}
                onClick={() => handleSelect(item)}
                className={`group p-2.5 rounded-xl text-left border transition-all flex flex-col justify-between relative ${
                  isSelected
                    ? 'bg-gradient-to-r from-bloop-600/30 via-quantum-600/20 to-slate-900 border-bloop-500/80 shadow-md shadow-bloop-500/20'
                    : 'bg-slate-950/40 hover:bg-slate-900/80 border-white/5 hover:border-white/20'
                }`}
              >
                <div className="flex items-start justify-between gap-1.5 mb-1">
                  <div className="flex items-center space-x-2">
                    <span
                      className={`text-[11px] font-mono font-bold w-5 h-5 rounded flex items-center justify-center ${
                        isSelected
                          ? 'bg-bloop-500 text-white'
                          : 'bg-slate-900 text-slate-400 group-hover:text-slate-200 border border-white/10'
                      }`}
                    >
                      {item.id}
                    </span>
                    <span
                      className={`text-xs font-bold tracking-tight ${
                        isSelected ? 'text-white' : 'text-slate-200 group-hover:text-white'
                      }`}
                    >
                      {item.name}
                    </span>
                  </div>

                  {isSelected && (
                    <span className="w-4 h-4 rounded-full bg-bloop-500 text-white flex items-center justify-center shrink-0">
                      <Check className="w-3 h-3" />
                    </span>
                  )}
                </div>

                <p className="text-[11px] text-slate-400 leading-snug font-sans group-hover:text-slate-300 line-clamp-2">
                  {item.description}
                </p>

                {/* Micro tags */}
                <div className="mt-2 flex items-center justify-between text-[10px] text-slate-500 border-t border-white/5 pt-1.5">
                  <span className="truncate max-w-[120px]">{item.category}</span>
                  <span className="font-mono">
                    {item.pitchOffsetHz && item.pitchOffsetHz > 0
                      ? `+${item.pitchOffsetHz}Hz`
                      : `${item.pitchOffsetHz || 0}Hz`}
                  </span>
                </div>
              </button>
            );
          })
        )}
      </div>

      {/* Expand / Collapse and Stats Footer */}
      <div className="flex items-center justify-between border-t border-white/5 pt-2.5 text-xs text-slate-400 relative z-10">
        <span className="text-[11px]">
          Showing <strong className="text-slate-200">{filteredEmotions.length}</strong> of{' '}
          <strong className="text-slate-200">{EMOTIONS.length}</strong> emotions
        </span>

        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center space-x-1 text-xs text-bloop-400 hover:text-bloop-300 font-medium transition"
        >
          <span>{isExpanded ? 'Collapse View' : 'Expand All 77 Emotions'}</span>
          {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>
      </div>
    </div>
  );
};
