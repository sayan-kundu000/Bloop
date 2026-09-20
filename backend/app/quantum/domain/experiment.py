"""
Bloop Quantum Experiment Domain Entity
Represents an experiment entity independent of persistence layer implementation.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from backend.app.quantum.domain.models import ExperimentType, ExecutionStatus, QuantumFramework


class QuantumExperimentData(BaseModel):
    id: Optional[int] = None
    user_id: Optional[int] = None
    experiment_type: ExperimentType
    title: str
    description: Optional[str] = None
    framework: QuantumFramework = QuantumFramework.QISKIT
    backend: str = "aer_simulator"
    status: ExecutionStatus = ExecutionStatus.COMPLETED
    qubits: int = 2
    shots: int = 1024
    input_payload: Dict[str, Any] = Field(default_factory=dict)
    results: Dict[str, Any] = Field(default_factory=dict)
    circuit_depth: int = 0
    execution_time_ms: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
