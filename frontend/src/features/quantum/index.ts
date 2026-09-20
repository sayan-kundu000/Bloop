/**
 * Quantum Intelligence Feature Module
 * Isolated UI boundary for Qiskit circuits, PennyLane QNN, semantic kernels, and benchmarks.
 */

export interface QuantumStateVector {
  qubits: number;
  depth: number;
  fidelity: number;
}

export interface QuantumTextClassificationResult {
  style: string;
  confidence: number;
  circuit_depth: number;
}

export interface QuantumEmotionAnalysisResult {
  emotion: string;
  confidence: number;
  entropy: number;
}
