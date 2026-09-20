/**
 * Language Feature Module
 * Manages supported locales, display names, and language codes.
 */

export interface Language {
  code: string;
  name: string;
  native_name?: string;
  is_supported: boolean;
}
