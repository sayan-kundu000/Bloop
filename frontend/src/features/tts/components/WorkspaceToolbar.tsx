import React, { useState } from 'react';
import { Trash2, Sparkles, Clipboard, Check } from 'lucide-react';
import { Button, ConfirmDialog } from '../../../components/ui';

export interface PresetSampleItem {
  label: string;
  text: string;
}

export const DEFAULT_PRESETS: PresetSampleItem[] = [
  {
    label: 'Standard',
    text: 'Welcome to Bloop. Experience high-fidelity artificial intelligence speech synthesis powered by dynamic voice orchestration and educational quantum computing algorithms.',
  },
  {
    label: 'Narration',
    text: 'The evening mist settled quietly over the valley as the distant bell echoed three times through the damp pines, signaling that the journey had only just begun.',
  },
  {
    label: 'Technical',
    text: 'All speech synthesis requests are validated through FastAPI before invoking provider pipelines. Quantum statevector simulations compute kernel fidelity without blocking audio delivery.',
  },
];

export interface WorkspaceToolbarProps {
  hasText: boolean;
  textLength: number;
  onClear: () => void;
  onLoadSample: (sampleText: string) => void;
  onPaste?: (pastedText: string) => void;
  disabled?: boolean;
}

export const WorkspaceToolbar: React.FC<WorkspaceToolbarProps> = ({
  hasText,
  textLength,
  onClear,
  onLoadSample,
  onPaste,
  disabled = false,
}) => {
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const [pasteSuccess, setPasteSuccess] = useState(false);

  const handleClearClick = () => {
    // Only prompt confirmation if text is substantial (> 100 characters)
    if (textLength > 100) {
      setIsConfirmOpen(true);
    } else {
      onClear();
    }
  };

  const handleConfirmClear = () => {
    setIsConfirmOpen(false);
    onClear();
  };

  const handlePasteClipboard = async () => {
    if (!onPaste) return;
    try {
      if (navigator.clipboard && navigator.clipboard.readText) {
        const clipboardText = await navigator.clipboard.readText();
        if (clipboardText) {
          onPaste(clipboardText);
          setPasteSuccess(true);
          setTimeout(() => setPasteSuccess(false), 2000);
        }
      }
    } catch {
      // Clipboard access denied or unsupported; user can use standard Ctrl+V / Cmd+V
    }
  };

  return (
    <div className="flex flex-wrap items-center justify-between gap-2 border-b border-white/5 pb-3">
      {/* Preset Samples */}
      <div className="flex flex-wrap items-center gap-1.5">
        <span className="text-xs text-slate-400 mr-1 hidden sm:inline">Presets:</span>
        {DEFAULT_PRESETS.map((sample) => (
          <button
            key={sample.label}
            type="button"
            onClick={() => onLoadSample(sample.text)}
            disabled={disabled}
            className="px-2.5 py-1 rounded-lg text-xs bg-slate-800/80 hover:bg-bloop-600/30 hover:text-bloop-300 text-slate-300 border border-white/5 transition disabled:opacity-50"
            title={`Load ${sample.label} sample`}
          >
            <Sparkles className="w-3 h-3 inline mr-1 text-bloop-400" aria-hidden="true" />
            {sample.label}
          </button>
        ))}
      </div>

      {/* Action Buttons */}
      <div className="flex items-center space-x-2">
        {onPaste && (
          <button
            type="button"
            onClick={handlePasteClipboard}
            disabled={disabled}
            className="px-2.5 py-1 text-xs text-slate-300 hover:text-white bg-slate-800/60 hover:bg-slate-700/60 border border-white/5 rounded-lg transition flex items-center space-x-1 disabled:opacity-50"
            title="Paste text from clipboard"
          >
            {pasteSuccess ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-400" aria-hidden="true" />
                <span className="text-emerald-400">Pasted</span>
              </>
            ) : (
              <>
                <Clipboard className="w-3.5 h-3.5 text-slate-400" aria-hidden="true" />
                <span>Paste</span>
              </>
            )}
          </button>
        )}

        {hasText && (
          <button
            type="button"
            onClick={handleClearClick}
            disabled={disabled}
            className="px-2.5 py-1 text-xs text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition flex items-center space-x-1 disabled:opacity-50"
            title="Clear text"
          >
            <Trash2 className="w-3.5 h-3.5" aria-hidden="true" />
            <span>Clear</span>
          </button>
        )}
      </div>

      {/* Confirmation Dialog for clearing long text */}
      <ConfirmDialog
        isOpen={isConfirmOpen}
        onClose={() => setIsConfirmOpen(false)}
        onConfirm={handleConfirmClear}
        title="Clear Speech Text"
        message="Are you sure you want to clear your current text? This action cannot be undone."
        confirmLabel="Clear Text"
        cancelLabel="Keep Text"
        isDestructive={true}
      />
    </div>
  );
};
