/**
 * Authentication Feature Module
 * Boundary for user authentication, JWT lifecycle, and auth session state.
 */

export interface AuthUser {
  id: string;
  email: string;
  full_name?: string;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
}
