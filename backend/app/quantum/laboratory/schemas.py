"""
Bloop Quantum Circuit & Noise Laboratory Schemas
Provides Pydantic request and response schemas for laboratory circuit simulation,
noise configuration, comparison experiments, and parameter sweeps.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, model_validator, field_validator


class GateOperationSchema(BaseModel):
    """Declarative specification for a single quantum gate."""
    gate: str = Field(..., description="Gate identifier (e.g., h, x, y, z, s, t, rx, ry, rz, cx, cz, swap)")
    target: int = Field(..., ge=0, description="Target qubit index")
    control: Optional[int] = Field(None, ge=0, description="Control qubit index for two-qubit gates")
    parameter: Optional[float] = Field(None, description="Angle in radians for parameterized rotations")

    @field_validator("gate")
    @classmethod
    def normalize_gate_name(cls, v: str) -> str:
        clean = v.lower().strip()
        if clean == "cnot":
            return "cx"
        return clean


class NoiseModelConfigSchema(BaseModel):
    """Detailed configuration for physical noise channels."""
    model: str = Field("depolarizing", description="Noise model type: depolarizing, bit_flip, phase_flip, bit_phase_flip, thermal_relaxation, readout_error")
    probability: Optional[float] = Field(None, ge=0.0, le=1.0, description="Error probability in [0.0, 1.0]")
    t1: Optional[float] = Field(None, gt=0.0, description="Thermal relaxation time T1 in microseconds")
    t2: Optional[float] = Field(None, gt=0.0, description="Dephasing time T2 in microseconds (must satisfy T2 <= 2*T1)")
    p0_given_1: Optional[float] = Field(None, ge=0.0, le=1.0, description="Probability of measuring 0 when state is 1")
    p1_given_0: Optional[float] = Field(None, ge=0.0, le=1.0, description="Probability of measuring 1 when state is 0")
    gate_time: Optional[float] = Field(None, gt=0.0, description="Single/two-qubit gate duration in microseconds")


class NoiseSweepConfigSchema(BaseModel):
    """Configuration for an ordered noise parameter sweep."""
    parameter: str = Field("probability", description="Sweep parameter (e.g. probability)")
    start: float = Field(0.0, ge=0.0, description="Starting parameter value")
    stop: float = Field(0.1, ge=0.0, description="Ending parameter value")
    step: float = Field(0.02, gt=0.0, description="Step increment (must be strictly positive)")

    @model_validator(mode="after")
    def validate_bounds(self) -> "NoiseSweepConfigSchema":
        if self.stop < self.start:
            raise ValueError(f"Sweep stop value ({self.stop}) must be >= start value ({self.start})")
        # Ensure bounded steps
        steps = int(round((self.stop - self.start) / self.step)) + 1
        if steps > 10:
            raise ValueError(f"Sweep would generate {steps} points; maximum allowed is 10 points.")
        return self


class CircuitLabRequestSchema(BaseModel):
    """Request schema for standard circuit execution (Mode A or Mode B)."""
    num_qubits: int = Field(2, ge=1, le=8, description="Number of qubits in register")
    qubits: Optional[int] = Field(None, ge=1, le=8, description="Alias for num_qubits")
    gates: List[GateOperationSchema] = Field(default_factory=list, description="Sequence of quantum gates")
    preset: Optional[str] = Field(None, description="Preset circuit template name")
    framework: Optional[str] = Field("qiskit", description="Simulation framework ('qiskit' or 'pennylane')")
    shots: int = Field(1024, ge=100, le=8192, description="Number of measurement shots")
    noise_level: float = Field(0.0, ge=0.0, le=0.5, description="Legacy simple depolarizing noise level")
    noise: Optional[NoiseModelConfigSchema] = Field(None, description="Granular noise channel configuration")
    noise_profile: Optional[str] = Field(None, description="Preset noise profile: ideal, low_noise, medium_noise, high_noise")
    seed: Optional[int] = Field(None, description="Optional random seed for reproducible stochastic simulation")

    @model_validator(mode="before")
    @classmethod
    def resolve_qubit_count(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "qubits" in data and "num_qubits" not in data:
                data["num_qubits"] = data["qubits"]
        return data


class CircuitLabResponseSchema(BaseModel):
    """Response schema for single circuit simulation."""
    num_qubits: int
    circuit_depth: int
    total_gates: int
    counts: Dict[str, int]
    probabilities: Dict[str, float]
    state_vector: Optional[List[str]] = None
    qasm: str
    circuit_diagram_ascii: str
    is_noisy_simulation: bool
    noise_model: Optional[str] = None
    execution_time_ms: float
    entropy: Optional[float] = None
    dominant_state: Optional[str] = None
    seed: Optional[int] = None
    framework: str = "qiskit"
    backend: str = "aer_simulator"


class CircuitComparisonRequestSchema(BaseModel):
    """Request schema for Mode C: Ideal vs Noisy Comparative Experiment."""
    num_qubits: int = Field(2, ge=1, le=8)
    gates: List[GateOperationSchema] = Field(default_factory=list)
    preset: Optional[str] = None
    shots: int = Field(1024, ge=100, le=8192)
    noise: Optional[NoiseModelConfigSchema] = None
    noise_profile: Optional[str] = Field("medium_noise", description="Preset noise profile to compare against ideal")
    seed: Optional[int] = None


class StateComparisonEntry(BaseModel):
    """Single basis state comparison."""
    state: str
    ideal_count: int
    noisy_count: int
    ideal_probability: float
    noisy_probability: float
    divergence: float


class CircuitComparisonResponseSchema(BaseModel):
    """Response schema for Mode C: Comparative Experiment."""
    num_qubits: int
    circuit_depth: int
    total_gates: int
    ideal_counts: Dict[str, int]
    noisy_counts: Dict[str, int]
    ideal_probabilities: Dict[str, float]
    noisy_probabilities: Dict[str, float]
    total_variation_distance: float
    classical_fidelity: float
    ideal_entropy: float
    noisy_entropy: float
    max_divergence: float
    dominant_ideal_state: str
    dominant_noisy_state: str
    states_comparison: List[StateComparisonEntry]
    circuit_diagram_ascii: str
    noise_model: str
    execution_time_ms: float


class CircuitRobustnessRequestSchema(BaseModel):
    """Request schema for Mode D: Robustness Experiment across noise sweep."""
    num_qubits: int = Field(2, ge=1, le=8)
    gates: List[GateOperationSchema] = Field(default_factory=list)
    preset: Optional[str] = None
    shots: int = Field(1024, ge=100, le=4096)
    noise_model: str = Field("depolarizing", description="Noise channel to sweep (e.g., depolarizing, bit_flip, phase_flip, readout_error)")
    sweep: NoiseSweepConfigSchema = Field(default_factory=NoiseSweepConfigSchema)
    target_state: Optional[str] = Field(None, description="Optional target state (e.g. '00', '11') to track success probability")
    repeats_per_point: int = Field(1, ge=1, le=5, description="Number of repetitions per point for variance estimation")
    seed: Optional[int] = None


class RobustnessPointSchema(BaseModel):
    """Data point in the robustness sweep curve."""
    parameter_value: float
    mean_fidelity: float
    std_fidelity: float
    mean_tvd: float
    std_tvd: float
    success_probability: float
    execution_time_ms: float
    repetition_count: int


class CircuitRobustnessResponseSchema(BaseModel):
    """Response schema for Mode D: Robustness Experiment."""
    sweep_parameter: str
    points: List[RobustnessPointSchema]
    target_state: Optional[str]
    baseline_ideal_state: str
    circuit_depth: int
    total_gates: int
    total_runs: int
    total_execution_time_ms: float
    summary: str


class TemplateInfoSchema(BaseModel):
    """Information schema for a pre-defined circuit template."""
    id: str
    name: str
    description: str
    qubits: int
    depth: int
    gate_count: int
    gates: List[GateOperationSchema]
    expected_support: List[str]


class NoiseProfileInfoSchema(BaseModel):
    """Information schema for a standard noise profile."""
    id: str
    name: str
    description: str
    model: str
    probability: float
    readout_error: float
