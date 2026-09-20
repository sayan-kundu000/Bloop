import { apiClient } from '../../../api/client';
import { ApiResponse, Language, Voice, TTSResponse, TextStats } from '../../../types';
import { TTSGenerationPayload } from '../types/tts.types';

export const ttsFeatureApi = {
  /**
   * Dynamically retrieves all active application languages from the backend.
   */
  getLanguages: async (): Promise<Language[]> => {
    const { data } = await apiClient.get<ApiResponse<Language[]>>('/languages');
    return data.data || [];
  },

  /**
   * Dynamically retrieves voices from the backend, supporting optional language, gender, and search filtering.
   */
  getVoices: async (params?: { language_code?: string; gender?: string; search?: string }): Promise<Voice[]> => {
    const { data } = await apiClient.get<ApiResponse<Voice[]>>('/voices', { params });
    return data.data || [];
  },

  /**
   * Client text analysis endpoint
   */
  analyzeText: async (text: string): Promise<TextStats> => {
    const { data } = await apiClient.post<ApiResponse<TextStats>>('/tts/analyze', { text });
    return data.data!;
  },

  /**
   * Core speech synthesis generation request
   */
  generateSpeech: async (payload: TTSGenerationPayload): Promise<TTSResponse> => {
    const { data } = await apiClient.post<ApiResponse<TTSResponse>>('/tts', payload);
    return data.data!;
  },
};
