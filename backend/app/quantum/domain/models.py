"""
Bloop Quantum Domain Models
Defines domain enums and value types for quantum execution, gate types,
frameworks, and lifecycle states.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ExperimentType(str, Enum):
    BASIC_CIRCUIT = "basic_circuit"
    QUANTUM_TEXT = "quantum_text"
    QUANTUM_EMOTION = "quantum_emotion"
    QUANTUM_SEMANTIC = "quantum_semantic"
    HYBRID_ML = "hybrid_ml"
    BENCHMARK = "benchmark"


class QuantumFramework(str, Enum):
    QISKIT = "qiskit"
    PENNYLANE = "pennylane"
    HYBRID_ML = "hybrid_ml"


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class GateType(str, Enum):
    H = "h"
    X = "x"
    Y = "y"
    Z = "z"
    S = "s"
    T = "t"
    CX = "cx"
    CZ = "cz"
    SWAP = "swap"
    RX = "rx"
    RY = "ry"
    RZ = "rz"


class GateSpecification(BaseModel):
    gate: GateType
    target: int = Field(..., ge=0, description="Target qubit index")
    control: Optional[int] = Field(None, ge=0, description="Control qubit index for multi-qubit gates")
    parameter: Optional[float] = Field(None, description="Rotation angle in radians for parameterized gates")
