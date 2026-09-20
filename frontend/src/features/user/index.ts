/**
 * User Profile & Settings Feature Module
 */

export interface UserProfile {
  id: string;
  email: string;
  full_name?: string;
  default_language_code?: string;
  default_voice_id?: string;
  created_at: string;
}
