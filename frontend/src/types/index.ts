export interface ApiSuccess<T> {
  success: true;
  data: T;
  message?: string;
}

export interface ApiErrorData {
  code: string;
  message: string;
  details?: unknown;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: ApiErrorData;
  message?: string;
}

export interface PaginationMeta {
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
}

export interface User {
  id: number;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
}

export interface UserPreference {
  id: number;
  user_id: number;
  theme: 'dark' | 'light' | 'system';
  audio_speed: number;
  auto_play: boolean;
  default_language_code?: string | null;
  default_voice_id?: string | null;
}

export interface UserDetail extends User {
  preference?: UserPreference;
}

export interface UpdateProfilePayload {
  full_name?: string;
}

export interface UpdatePreferencesPayload {
  theme?: 'dark' | 'light' | 'system';
  audio_speed?: number;
  auto_play?: boolean;
  default_language_code?: string | null;
  default_voice_id?: string | null;
}


export interface Token {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Language {
  code: string;
  name: string;
  native_name?: string;
  is_active: boolean;
}

export interface Voice {
  id: number;
  voice_id: string;
  name: string;
  language_code: string;
  supported_languages?: string[];
  gender: 'female' | 'male' | 'neutral' | 'unspecified';
  accent?: string;
  description?: string;
  provider: string;
  preview_url?: string;
  is_active: boolean;
  is_user_configured: boolean;
}

export interface TTSRequest {
  text: string;
  language: string;
  voice_id: string;
  speed?: number;
  pitch?: number;
  emotion?: string;
}

export interface AudioVideoReference {
  media_title: string;
  scene_timestamp?: string;
  clip_timestamp?: string;
  scene_context: string;
  acoustic_benchmark?: {
    f0_median_hz?: number;
    formant_f1_hz?: number;
    formant_f2_hz?: number;
    tempo_wpm?: number;
    vocal_grit?: number;
    spatial_acoustic?: string;
  };
}

export interface QuantumDecisionDetails {
  pauli_z_expectations: number[];
  decided_pitch_hz: number;
  decided_rate_pct: number;
  decided_dsp_filter: string;
  decided_delivery_mode: string;
  decision_rationale: string;
}

export interface QuantumResonanceMetrics {
  quantum_fidelity: number;
  quantum_emotion: string;
  entanglement_entropy: number;
  resonance_verdict: string;
  canonical_source: string;
  applied_dsp_filter: string;
  effective_pitch?: string;
  effective_rate?: string;
  audio_video_reference?: AudioVideoReference;
  quantum_decision?: QuantumDecisionDetails;
}

export interface TTSResponse {
  generation_id?: number;
  audio_url: string;
  download_url: string;
  text: string;
  char_count: number;
  word_count: number;
  language: string;
  voice_id: string;
  voice_name?: string;
  duration_seconds: number;
  provider: string;
  is_simulation: boolean;
  emotion?: string;
  emotion_id?: number;
  content_type?: string;
  audio_format?: string;
  quantum_metrics?: QuantumResonanceMetrics;
}

export interface TextStats {
  char_count: number;
  word_count: number;
  estimated_duration_seconds: number;
  is_valid: boolean;
  error_message?: string;
}

export interface SpeechGeneration {
  id: number;
  user_id?: number;
  text: string;
  char_count: number;
  word_count: number;
  language_code: string;
  voice_id: string;
  voice_name?: string;
  audio_url: string;
  download_url: string;
  duration_seconds: number;
  file_size_bytes: number;
  provider: string;
  is_favorite: boolean;
  favorite_id?: number;
  created_at: string;
}

export interface Favorite {
  id: number;
  user_id: number;
  generation_id: number;
  label?: string;
  created_at: string;
  generation?: SpeechGeneration;
}

// Quantum Types
export interface QuantumTextResult {
  input_text: string;
  tokens: string[];
  classical_features: number[];
  quantum_probabilities: Record<string, number>;
  predicted_style: string;
  confidence: number;
  classical_baseline_prediction: string;
  classical_confidence: number;
  circuit_depth: number;
  num_qubits: number;
  execution_time_ms: number;
}

export interface QuantumEmotionResult {
  input_text: string;
  detected_emotion: 'joy' | 'sadness' | 'anger' | 'neutral';
  emotion_scores: Record<string, number>;
  quantum_probabilities: Record<string, number>;
  hybrid_qnn_confidence: number;
  classical_baseline_emotion: string;
  classical_confidence: number;
  entanglement_entropy: number;
  circuit_depth: number;
  num_qubits: number;
  execution_time_ms: number;
}

export interface QuantumSemanticResult {
  text_a: string;
  text_b: string;
  quantum_kernel_similarity: number;
  classical_cosine_similarity: number;
  similarity_verdict: string;
  divergence: number;
  num_qubits: number;
  circuit_depth: number;
  execution_time_ms: number;
  method?: string;
  similarity_score?: number;
  classical_similarity?: number;
  quantum_similarity?: number | null;
  hybrid_similarity?: number | null;
  semantic_distance?: number;
  feature_dimension?: number;
  reduced_dimension?: number;
  representation_method?: string;
  reduction_method?: string;
  encoding_method?: string;
  quantum_framework?: string;
  quantum_backend?: string;
  shots?: number;
  experiment_id?: string;
  pipeline_steps?: string[];
  details?: Record<string, any>;
}

export interface GateOperation {
  gate: string;
  target: number;
  control?: number;
  parameter?: number;
}

export interface QuantumCircuitResult {
  num_qubits: number;
  circuit_depth: number;
  total_gates: number;
  counts: Record<string, number>;
  probabilities: Record<string, number>;
  state_vector?: string[];
  qasm: string;
  circuit_diagram_ascii: string;
  is_noisy_simulation: boolean;
  noise_model?: string;
  execution_time_ms: number;
  entropy?: number;
  dominant_state?: string;
  seed?: number;
  framework?: string;
  backend?: string;
}

export interface StateComparisonEntry {
  state: string;
  ideal_count: number;
  noisy_count: number;
  ideal_probability: number;
  noisy_probability: number;
  divergence: number;
}

export interface CircuitComparisonResult {
  num_qubits: number;
  circuit_depth: number;
  total_gates: number;
  ideal_counts: Record<string, number>;
  noisy_counts: Record<string, number>;
  ideal_probabilities: Record<string, number>;
  noisy_probabilities: Record<string, number>;
  total_variation_distance: number;
  classical_fidelity: number;
  ideal_entropy: number;
  noisy_entropy: number;
  max_divergence: number;
  dominant_ideal_state: string;
  dominant_noisy_state: string;
  states_comparison: StateComparisonEntry[];
  circuit_diagram_ascii: string;
  noise_model: string;
  execution_time_ms: number;
}

export interface RobustnessPoint {
  parameter_value: number;
  mean_fidelity: number;
  std_fidelity: number;
  mean_tvd: number;
  std_tvd: number;
  success_probability: number;
  execution_time_ms: number;
  repetition_count: number;
}

export interface CircuitRobustnessResult {
  sweep_parameter: string;
  points: RobustnessPoint[];
  target_state?: string;
  baseline_ideal_state: string;
  circuit_depth: number;
  total_gates: number;
  total_runs: number;
  total_execution_time_ms: number;
  summary: string;
}

export interface TemplateInfo {
  id: string;
  name: string;
  description: string;
  qubits: number;
  depth: number;
  gate_count: number;
  gates: GateOperation[];
  expected_support: string[];
}

export interface NoiseProfileInfo {
  id: string;
  name: string;
  description: string;
  model: string;
  probability: number;
  readout_error: number;
}

export interface NoiseModelConfig {
  model: string;
  probability?: number;
  t1?: number;
  t2?: number;
  p0_given_1?: number;
  p1_given_0?: number;
  gate_time?: number;
}

export interface MetricComparison {
  accuracy?: number;
  precision?: number;
  recall?: number;
  f1_score?: number;
  mae?: number;
  rmse?: number;
  correlation?: number;
  training_time_seconds?: number;
  inference_time_seconds: number;
  qubits?: number;
  shots?: number;
  circuit_depth?: number;
  tvd?: number;
  fidelity?: number;
}

export interface PipelineExecutionBreakdown {
  classical_ms: number;
  quantum_ms: number;
  fusion_ms: number;
  recommendation_ms: number;
  total_ms: number;
}

export interface SpeechRecommendation {
  style: string;
  speed: number;
  pitch: number;
  stability: number;
  similarity_boost: number;
  pacing: string;
  reason: string;
  confidence?: number;
  applied: boolean;
  target_voice_id?: string;
  validated_compatible: boolean;
}

export interface BenchmarkCategoryInfo {
  category: string;
  name: string;
  description: string;
  classical_baseline: string;
  quantum_candidate: string;
  measured_metrics: string[];
}

export interface QuantumBenchmarkResult {
  category?: string;
  dataset?: Record<string, any>;
  classical_model: string;
  quantum_model: string;
  hybrid_model?: string;
  classical_metrics: MetricComparison;
  quantum_metrics: MetricComparison;
  hybrid_metrics?: MetricComparison;
  resource_usage?: Record<string, any>;
  honest_analysis: string;
  quantum_advantage_detected: boolean;
  summary: string;
  pipeline_breakdown?: PipelineExecutionBreakdown;
  speech_recommendation?: SpeechRecommendation;
}

export interface HybridAnalysisResult {
  input_text: string;
  classical_prediction: Record<string, any>;
  quantum_prediction: Record<string, any>;
  hybrid_prediction: Record<string, any>;
  confidence?: number;
  fusion_method: string;
  fusion_weights: Record<string, number>;
  speech_recommendation?: SpeechRecommendation;
  pipeline_breakdown: PipelineExecutionBreakdown;
  fallback_used: boolean;
}
