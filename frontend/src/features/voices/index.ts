/**
 * Voice Feature Module
 * Voice catalog, dynamic voice registration, filtering, and previewing.
 */

export interface VoiceModel {
  id: string;
  name: string;
  language_code: string;
  provider: string;
  category?: string;
  description?: string;
  gender?: 'male' | 'female' | 'neutral';
  preview_url?: string;
}
