import { vi } from 'vitest';
import { mockUser, mockPreferences, mockDynamicVoices, mockLanguages } from '../fixtures';

export const mockAuthApi = {
  login: vi.fn().mockResolvedValue({
    access_token: 'mock-jwt-token-xyz',
    token_type: 'bearer',
    user: mockUser,
  }),
  register: vi.fn().mockResolvedValue({
    access_token: 'mock-jwt-token-xyz',
    token_type: 'bearer',
    user: mockUser,
  }),
  getCurrentUser: vi.fn().mockResolvedValue(mockUser),
  logout: vi.fn().mockResolvedValue(undefined),
};

export const mockVoiceApi = {
  getLanguages: vi.fn().mockResolvedValue(mockLanguages),
  getVoices: vi.fn().mockResolvedValue(mockDynamicVoices),
};

export const mockUserApi = {
  getProfile: vi.fn().mockResolvedValue({ ...mockUser, preference: mockPreferences }),
  getPreferences: vi.fn().mockResolvedValue(mockPreferences),
};
