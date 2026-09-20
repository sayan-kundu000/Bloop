"""
Bloop Quantum Circuit & Noise Laboratory Subsystem
Provides isolated experimental and educational environment for constructing bounded quantum circuits,
applying controlled noise models, comparing ideal vs noisy executions, and conducting robustness sweeps.
"""

from backend.app.quantum.laboratory.service import QuantumLaboratoryService
from backend.app.quantum.laboratory.models import (
    LaboratoryMode,
    NoiseModelType,
    NoiseProfile,
    SupportedGate,
    DistributionComparisonResult,
    RobustnessSweepResult,
    RobustnessPoint,
    MeasurementSummary,
)
from backend.app.quantum.laboratory.schemas import (
    GateOperationSchema,
    NoiseModelConfigSchema,
    NoiseSweepConfigSchema,
    CircuitLabRequestSchema,
    CircuitLabResponseSchema,
    CircuitComparisonRequestSchema,
    CircuitComparisonResponseSchema,
    CircuitRobustnessRequestSchema,
    CircuitRobustnessResponseSchema,
    TemplateInfoSchema,
    NoiseProfileInfoSchema,
)
from backend.app.quantum.laboratory.exceptions import (
    CircuitInvalidException,
    UnsupportedGateException,
    InvalidQubitIndexException,
    InvalidGateParameterException,
    CircuitTooLargeException,
    CircuitTooDeepException,
    NoiseModelInvalidException,
    NoiseParameterInvalidException,
    NoiseSweepTooLargeException,
    ExperimentTooLargeException,
    SimulatorUnavailableException,
    ResultAnalysisFailedException,
)

__all__ = [
    "QuantumLaboratoryService",
    "LaboratoryMode",
    "NoiseModelType",
    "NoiseProfile",
    "SupportedGate",
    "DistributionComparisonResult",
    "RobustnessSweepResult",
    "RobustnessPoint",
    "MeasurementSummary",
    "GateOperationSchema",
    "NoiseModelConfigSchema",
    "NoiseSweepConfigSchema",
    "CircuitLabRequestSchema",
    "CircuitLabResponseSchema",
    "CircuitComparisonRequestSchema",
    "CircuitComparisonResponseSchema",
    "CircuitRobustnessRequestSchema",
    "CircuitRobustnessResponseSchema",
    "TemplateInfoSchema",
    "NoiseProfileInfoSchema",
    "CircuitInvalidException",
    "UnsupportedGateException",
    "InvalidQubitIndexException",
    "InvalidGateParameterException",
    "CircuitTooLargeException",
    "CircuitTooDeepException",
    "NoiseModelInvalidException",
    "NoiseParameterInvalidException",
    "NoiseSweepTooLargeException",
    "ExperimentTooLargeException",
    "SimulatorUnavailableException",
    "ResultAnalysisFailedException",
]
