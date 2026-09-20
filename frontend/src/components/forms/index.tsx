import React from 'react';

export interface FormFieldProps {
  label: string;
  id?: string;
  error?: string;
  helpText?: string;
  required?: boolean;
  children: React.ReactNode;
}

export const FormField: React.FC<FormFieldProps> = ({
  label,
  id,
  error,
  helpText,
  required = false,
  children,
}) => {
  return (
    <div className="flex flex-col space-y-1.5 mb-4">
      <label htmlFor={id} className="text-xs font-semibold uppercase tracking-wider text-slate-400">
        {label}
        {required && <span className="ml-1 text-rose-500">*</span>}
      </label>
      {children}
      {helpText && !error && <p className="text-xs text-slate-500">{helpText}</p>}
      {error && <p className="text-xs text-rose-400 font-medium">{error}</p>}
    </div>
  );
};
