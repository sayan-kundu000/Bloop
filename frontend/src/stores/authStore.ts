import { create } from 'zustand';
import { User } from '../types';
import { authApi } from '../api/client';
import { queryClient } from '../lib/queryClient';
import { useAudioStore } from './audioStore';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, pass: string) => Promise<void>;
  register: (email: string, pass: string, name?: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem('bloop_token'),
  isAuthenticated: !!localStorage.getItem('bloop_token'),
  isLoading: true,

  login: async (email, password) => {
    const data = await authApi.login({ email, password });
    localStorage.setItem('bloop_token', data.access_token);
    set({ user: data.user, token: data.access_token, isAuthenticated: true });
  },

  register: async (email, password, full_name) => {
    const data = await authApi.register({ email, password, full_name });
    localStorage.setItem('bloop_token', data.access_token);
    set({ user: data.user, token: data.access_token, isAuthenticated: true });
  },

  logout: () => {
    // Attempt backend logout notice without blocking frontend teardown
    authApi.logout().catch(() => {});

    // Clear authentication token
    localStorage.removeItem('bloop_token');

    // Halt active audio playback
    useAudioStore.getState().stopAudio();

    // Clear all cached server state to prevent user data leakage between browser sessions
    queryClient.clear();

    set({ user: null, token: null, isAuthenticated: false });
  },

  checkAuth: async () => {
    const token = localStorage.getItem('bloop_token');
    if (!token) {
      set({ user: null, token: null, isAuthenticated: false, isLoading: false });
      return;
    }
    try {
      const user = await authApi.getCurrentUser();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch {
      localStorage.removeItem('bloop_token');
      queryClient.clear();
      set({ user: null, token: null, isAuthenticated: false, isLoading: false });
    }
  },
}));

