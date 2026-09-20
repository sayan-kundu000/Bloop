/**
 * Centralized API Service abstractions
 */
import { apiClient } from '../api/client';

export const healthService = {
  checkHealth: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },
};

export const languagesService = {
  getLanguages: async () => {
    const response = await apiClient.get('/languages');
    return response.data;
  },
};

export const voicesService = {
  getVoices: async (languageCode?: string) => {
    const params = languageCode ? { language_code: languageCode } : {};
    const response = await apiClient.get('/voices', { params });
    return response.data;
  },
};
