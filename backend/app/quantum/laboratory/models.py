"""
Bloop Quantum Circuit & Noise Laboratory Models
Defines domain types, enums, dataclasses, and analysis structures for the laboratory subsystem.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class LaboratoryMode(str, Enum):
    IDEAL = "ideal"
    NOISY = "noisy"
    COMPARISON = "comparison"
    ROBUSTNESS = "robustness"


class NoiseModelType(str, Enum):
    DEPOLARIZING = "depolarizing"
    BIT_FLIP = "bit_flip"
    PHASE_FLIP = "phase_flip"
    BIT_PHASE_FLIP = "bit_phase_flip"
    THERMAL_RELAXATION = "thermal_relaxation"
    READOUT_ERROR = "readout_error"


class NoiseProfile(str, Enum):
    IDEAL = "ideal"
    LOW_NOISE = "low_noise"
    MEDIUM_NOISE = "medium_noise"
    HIGH_NOISE = "high_noise"


class SupportedGate(str, Enum):
    H = "h"
    X = "x"
    Y = "y"
    Z = "z"
    S = "s"
    T = "t"
    RX = "rx"
    RY = "ry"
    RZ = "rz"
    CX = "cx"
    CZ = "cz"
    SWAP = "swap"


@dataclass(frozen=True)
class GateDefinition:
    """Represents a validated quantum gate primitive."""
    gate: str
    target: int
    control: Optional[int] = None
    parameter: Optional[float] = None


@dataclass
class NoiseConfig:
    """Validated noise parameters."""
    model: NoiseModelType
    probability: Optional[float] = None
    t1: Optional[float] = None
    t2: Optional[float] = None
    p0_given_1: Optional[float] = None
    p1_given_0: Optional[float] = None
    gate_time: Optional[float] = None


@dataclass
class MeasurementSummary:
    """Statistical summary of discrete measurement outcomes."""
    counts: Dict[str, int]
    probabilities: Dict[str, float]
    dominant_state: str
    dominant_probability: float
    entropy: float
    support_size: int


@dataclass
class DistributionComparisonResult:
    """Comparative similarity metrics between ideal and noisy distributions."""
    total_variation_distance: float
    classical_fidelity: float
    ideal_entropy: float
    noisy_entropy: float
    max_divergence: float
    dominant_ideal_state: str
    dominant_noisy_state: str
    states_comparison: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class RobustnessPoint:
    """A single observation point in a noise parameter sweep."""
    parameter_value: float
    mean_fidelity: float
    std_fidelity: float
    mean_tvd: float
    std_tvd: float
    success_probability: float
    execution_time_ms: float
    repetition_count: int = 1


@dataclass
class RobustnessSweepResult:
    """Aggregated results across an entire parameter sweep."""
    sweep_parameter: str
    points: List[RobustnessPoint]
    target_state: Optional[str]
    circuit_depth: int
    total_gates: int
    total_runs: int
    total_execution_time_ms: float
    summary: str


@dataclass
class CircuitExecutionResult:
    """Normalized output of a single laboratory circuit run."""
    num_qubits: int
    circuit_depth: int
    total_gates: int
    counts: Dict[str, int]
    probabilities: Dict[str, float]
    state_vector: Optional[List[str]] = None
    qasm: str = ""
    circuit_diagram_ascii: str = ""
    is_noisy: bool = False
    noise_model: Optional[str] = None
    execution_time_ms: float = 0.0
    seed: Optional[int] = None
    framework: str = "qiskit"
    backend: str = "aer_simulator"
    entropy: float = 0.0
    dominant_state: str = ""
