import axios from 'axios';
import {
  ApiResponse,
  PaginatedResponse,
  Token,
  User,
  UserDetail,
  UserPreference,
  UpdateProfilePayload,
  UpdatePreferencesPayload,
  Language,
  Voice,
  TTSRequest,
  TTSResponse,
  TextStats,
  SpeechGeneration,
  Favorite,
  QuantumTextResult,
  QuantumEmotionResult,
  QuantumSemanticResult,
  QuantumCircuitResult,
  QuantumBenchmarkResult,
  GateOperation,
  CircuitComparisonResult,
  CircuitRobustnessResult,
  TemplateInfo,
  NoiseProfileInfo,
  BenchmarkCategoryInfo,
  HybridAnalysisResult,
  SpeechRecommendation,
} from '../types';
import { config as appConfig } from '../app/config';
import { FrontendApiError, normalizeApiError } from '../lib/api/errors';

export { FrontendApiError, normalizeApiError };

export const apiClient = axios.create({
  baseURL: appConfig.apiV1Url,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach JWT token from localStorage if available
apiClient.interceptors.request.use((reqConfig) => {
  const token = localStorage.getItem('bloop_token');
  if (token && reqConfig.headers) {
    reqConfig.headers.Authorization = `Bearer ${token}`;
  }
  return reqConfig;
});

// Standard response interceptor with normalized error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const normalized = normalizeApiError(error);

    // If 401 Unauthorized, safely clear stale token if present
    if (normalized.status === 401) {
      if (typeof window !== 'undefined' && localStorage.getItem('bloop_token')) {
        localStorage.removeItem('bloop_token');
      }
    }

    return Promise.reject(normalized);
  }
);

// --- Auth APIs ---
export const authApi = {
  register: async (payload: { email: string; password: string; full_name?: string }): Promise<Token> => {
    const { data } = await apiClient.post<ApiResponse<Token>>('/auth/register', payload);
    return data.data!;
  },
  login: async (payload: { email: string; password: string }): Promise<Token> => {
    const { data } = await apiClient.post<ApiResponse<Token>>('/auth/login', payload);
    return data.data!;
  },
  getCurrentUser: async (): Promise<User> => {
    const { data } = await apiClient.get<ApiResponse<User>>('/auth/me');
    return data.data!;
  },
  logout: async (): Promise<void> => {
    await apiClient.post('/auth/logout');
  },
};

// --- User Profile & Preferences APIs ---
export const userApi = {
  getProfile: async (): Promise<UserDetail> => {
    const { data } = await apiClient.get<ApiResponse<UserDetail>>('/users/me');
    return data.data!;
  },
  updateProfile: async (payload: UpdateProfilePayload): Promise<UserDetail> => {
    const { data } = await apiClient.patch<ApiResponse<UserDetail>>('/users/me', payload);
    return data.data!;
  },
  getPreferences: async (): Promise<UserPreference> => {
    const { data } = await apiClient.get<ApiResponse<UserPreference>>('/users/me/preferences');
    return data.data!;
  },
  updatePreferences: async (payload: UpdatePreferencesPayload): Promise<UserPreference> => {
    const { data } = await apiClient.patch<ApiResponse<UserPreference>>('/users/me/preferences', payload);
    return data.data!;
  },
};


// --- Languages & Voices APIs ---
export const voiceApi = {
  getLanguages: async (): Promise<Language[]> => {
    const { data } = await apiClient.get<ApiResponse<Language[]>>('/languages');
    return data.data || [];
  },
  getVoices: async (params?: { language_code?: string; gender?: string; search?: string }): Promise<Voice[]> => {
    const { data } = await apiClient.get<ApiResponse<Voice[]>>('/voices', { params });
    return data.data || [];
  },
  registerVoice: async (voiceData: Partial<Voice>): Promise<Voice> => {
    const { data } = await apiClient.post<ApiResponse<Voice>>('/voices', voiceData);
    return data.data!;
  },
};

// --- TTS APIs ---
export const ttsApi = {
  analyzeText: async (text: string): Promise<TextStats> => {
    const { data } = await apiClient.post<ApiResponse<TextStats>>('/tts/analyze', { text });
    return data.data!;
  },
  generateSpeech: async (request: TTSRequest): Promise<TTSResponse> => {
    const { data } = await apiClient.post<ApiResponse<TTSResponse>>('/tts', request);
    return data.data!;
  },
  getAudioUrl: (relativeUrl: string): string => {
    if (relativeUrl.startsWith('http://') || relativeUrl.startsWith('https://')) {
      return relativeUrl;
    }
    return `${appConfig.apiBaseUrl}${relativeUrl}`;
  },
};

// --- History & Favorites APIs ---
export const historyApi = {
  getHistory: async (params?: {
    search?: string;
    language?: string;
    status?: string;
    favorite?: boolean;
    created_after?: string;
    created_before?: string;
    sort_by?: string;
    order?: string;
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<SpeechGeneration>> => {
    const { data } = await apiClient.get<ApiResponse<PaginatedResponse<SpeechGeneration>>>('/history', { params });
    return data.data!;
  },
  getGeneration: async (id: number): Promise<SpeechGeneration> => {
    const { data } = await apiClient.get<ApiResponse<SpeechGeneration>>(`/history/${id}`);
    return data.data!;
  },
  deleteGeneration: async (id: number): Promise<void> => {
    await apiClient.delete(`/history/${id}`);
  },

  getFavorites: async (params?: {
    search?: string;
    language?: string;
    page?: number;
    page_size?: number;
  } | number, pageSize = 20): Promise<PaginatedResponse<Favorite>> => {
    const queryParams = typeof params === 'number'
      ? { page: params, page_size: pageSize }
      : { page: 1, page_size: 20, ...params };
    const { data } = await apiClient.get<ApiResponse<PaginatedResponse<Favorite>>>('/favorites', {
      params: queryParams,
    });
    return data.data!;
  },
  addFavorite: async (generationId: number, label?: string): Promise<Favorite> => {
    const { data } = await apiClient.post<ApiResponse<Favorite>>('/favorites', {
      generation_id: generationId,
      label,
    });
    return data.data!;
  },
  removeFavorite: async (favoriteId: number): Promise<void> => {
    await apiClient.delete(`/favorites/${favoriteId}`);
  },
  removeFavoriteByGeneration: async (generationId: number): Promise<void> => {
    await apiClient.delete(`/favorites/generation/${generationId}`);
  },
};

// --- Quantum Intelligence APIs ---
export const quantumApi = {
  analyzeText: async (payload: { text: string; num_qubits?: number; shots?: number }): Promise<QuantumTextResult> => {
    const { data } = await apiClient.post<ApiResponse<QuantumTextResult>>('/quantum/text', payload);
    return data.data!;
  },
  analyzeEmotion: async (payload: { text: string; shots?: number }): Promise<QuantumEmotionResult> => {
    const { data } = await apiClient.post<ApiResponse<QuantumEmotionResult>>('/quantum/emotion', payload);
    return data.data!;
  },
  analyzeSemantics: async (payload: {
    text_a: string;
    text_b: string;
    num_qubits?: number;
    method?: string;
    framework?: string;
    shots?: number;
  }): Promise<QuantumSemanticResult> => {
    const { data } = await apiClient.post<ApiResponse<QuantumSemanticResult>>('/quantum/semantic', payload);
    return data.data!;
  },
  executeCircuit: async (payload: {
    num_qubits: number;
    gates: GateOperation[];
    preset?: string;
    shots?: number;
    noise_level?: number;
    noise_profile?: string;
    noise?: any;
    seed?: number;
  }): Promise<QuantumCircuitResult> => {
    const { data } = await apiClient.post<ApiResponse<QuantumCircuitResult>>('/quantum/circuit', payload);
    return data.data!;
  },
  compareCircuits: async (payload: {
    num_qubits: number;
    gates: GateOperation[];
    preset?: string;
    shots?: number;
    noise_profile?: string;
    noise?: any;
    seed?: number;
  }): Promise<CircuitComparisonResult> => {
    const { data } = await apiClient.post<ApiResponse<CircuitComparisonResult>>('/quantum/circuit/compare', payload);
    return data.data!;
  },
  runRobustness: async (payload: {
    num_qubits: number;
    gates: GateOperation[];
    preset?: string;
    shots?: number;
    noise_model?: string;
    sweep: { parameter: string; start: number; stop: number; step: number };
    repeats_per_point?: number;
    target_state?: string;
    seed?: number;
  }): Promise<CircuitRobustnessResult> => {
    const { data } = await apiClient.post<ApiResponse<CircuitRobustnessResult>>('/quantum/circuit/robustness', payload);
    return data.data!;
  },
  getCircuitTemplates: async (): Promise<TemplateInfo[]> => {
    const { data } = await apiClient.get<ApiResponse<TemplateInfo[]>>('/quantum/circuit/templates');
    return data.data || [];
  },
  getNoiseProfiles: async (): Promise<NoiseProfileInfo[]> => {
    const { data } = await apiClient.get<ApiResponse<NoiseProfileInfo[]>>('/quantum/circuit/noise-profiles');
    return data.data || [];
  },
  getCircuitGates: async (): Promise<any[]> => {
    const { data } = await apiClient.get<ApiResponse<any[]>>('/quantum/circuit/gates');
    return data.data || [];
  },
  runBenchmark: async (payload: {
    category?: string;
    dataset_size?: number;
    test_split?: number;
    num_qubits?: number;
    shots?: number;
    random_seed?: number;
    classical_weight?: number;
    quantum_weight?: number;
  }): Promise<QuantumBenchmarkResult> => {
    const { data } = await apiClient.post<ApiResponse<QuantumBenchmarkResult>>('/quantum/benchmark', payload);
    return data.data!;
  },
  getBenchmarkCategories: async (): Promise<BenchmarkCategoryInfo[]> => {
    const { data } = await apiClient.get<ApiResponse<BenchmarkCategoryInfo[]>>('/quantum/benchmark/categories');
    return data.data || [];
  },
  analyzeHybrid: async (payload: {
    text: string;
    target_voice_id?: string;
    language?: string;
    task?: string;
    fusion?: any;
    include_recommendation?: boolean;
    num_qubits?: number;
    shots?: number;
  }): Promise<HybridAnalysisResult> => {
    const { data } = await apiClient.post<ApiResponse<HybridAnalysisResult>>('/quantum/hybrid/analyze', payload);
    return data.data!;
  },
  getSpeechRecommendation: async (payload: {
    text: string;
    target_voice_id?: string;
    language?: string;
    predicted_emotion?: string;
    confidence?: number;
  }): Promise<SpeechRecommendation> => {
    const { data } = await apiClient.post<ApiResponse<SpeechRecommendation>>('/quantum/hybrid/recommend', payload);
    return data.data!;
  },
  getHistory: async (): Promise<any[]> => {
    const { data } = await apiClient.get<ApiResponse<any[]>>('/quantum/history');
    return data.data || [];
  },
};
