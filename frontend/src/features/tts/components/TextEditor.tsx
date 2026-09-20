import React from 'react';
import { FileText } from 'lucide-react';

export interface TextEditorProps {
  text: string;
  onChange: (newText: string) => void;
  isOverLimit?: boolean;
  disabled?: boolean;
  placeholder?: string;
}

export const TextEditor: React.FC<TextEditorProps> = ({
  text,
  onChange,
  isOverLimit = false,
  disabled = false,
  placeholder = 'Type or paste the words you want to synthesize into speech...',
}) => {
  return (
    <div className="flex flex-col space-y-2">
      <div className="flex items-center justify-between">
        <label
          htmlFor="bloop-text-editor"
          className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center space-x-1.5"
        >
          <FileText className="w-4 h-4 text-bloop-400" aria-hidden="true" />
          <span>Speech Text</span>
        </label>
      </div>

      <div className="relative">
        <textarea
          id="bloop-text-editor"
          name="speechText"
          value={text}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
          placeholder={placeholder}
          rows={7}
          className={`w-full bg-slate-950/70 text-slate-100 text-base rounded-xl p-4 border focus:outline-none transition resize-y min-h-[160px] placeholder-slate-500 leading-relaxed font-sans ${
            isOverLimit
              ? 'border-rose-500 focus:border-rose-400 focus:ring-1 focus:ring-rose-500/50'
              : 'border-white/10 focus:border-bloop-500/80 focus:ring-2 focus:ring-bloop-500/30'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
          aria-invalid={isOverLimit}
          aria-describedby="text-metrics-bar"
        />
      </div>
    </div>
  );
};
