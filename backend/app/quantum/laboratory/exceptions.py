"""
Bloop Quantum Circuit & Noise Laboratory Exceptions
Defines structured domain-level errors for circuit validation, noise model construction,
simulation execution, and result analysis.
"""

from typing import Any, Dict, Optional
from fastapi import status
from backend.app.core.exceptions import (
    BloopException,
    QuantumExecutionError,
    QuantumExecutionTimeoutException,
)


class CircuitInvalidException(BloopException):
    """Raised when circuit structure, gates, or targets are invalid."""

    def __init__(self, message: str = "Quantum circuit structure is invalid.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="CIRCUIT_INVALID",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class UnsupportedGateException(BloopException):
    """Raised when an unrecognized or unauthorized gate name is provided."""

    def __init__(self, message: str = "Requested gate is not supported.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="UNSUPPORTED_GATE",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class InvalidQubitIndexException(BloopException):
    """Raised when a target or control qubit index exceeds circuit register bounds."""

    def __init__(self, message: str = "Qubit index out of bounds.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="INVALID_QUBIT_INDEX",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class InvalidGateParameterException(BloopException):
    """Raised when a gate parameter (e.g. rotation angle) is invalid, NaN, or non-finite."""

    def __init__(self, message: str = "Gate parameter is invalid.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="INVALID_GATE_PARAMETER",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class CircuitTooLargeException(BloopException):
    """Raised when qubit count or total operations exceeds configured safety limits."""

    def __init__(self, message: str = "Circuit size exceeds computational limits.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="CIRCUIT_TOO_LARGE",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class CircuitTooDeepException(BloopException):
    """Raised when circuit depth exceeds configured depth boundaries."""

    def __init__(self, message: str = "Circuit depth exceeds computational limits.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="CIRCUIT_TOO_DEEP",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class NoiseModelInvalidException(BloopException):
    """Raised when a noise model type is unknown or improperly configured."""

    def __init__(self, message: str = "Noise model is invalid or unsupported.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="NOISE_MODEL_INVALID",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class NoiseParameterInvalidException(BloopException):
    """Raised when noise physical parameters (probabilities, T1/T2 times) violate constraints."""

    def __init__(self, message: str = "Noise model parameters violate physical boundaries.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="NOISE_PARAMETER_INVALID",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class NoiseSweepTooLargeException(BloopException):
    """Raised when requested noise parameter sweep exceeds maximum allowable sweep points."""

    def __init__(self, message: str = "Noise sweep step count exceeds configured boundary.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="NOISE_SWEEP_TOO_LARGE",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class ExperimentTooLargeException(BloopException):
    """Raised when cumulative experiment computational load (sweeps x repeats x shots) is too high."""

    def __init__(self, message: str = "Experiment complexity exceeds safety limits.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="EXPERIMENT_TOO_LARGE",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class SimulatorUnavailableException(BloopException):
    """Raised when AerSimulator or PennyLane device cannot be initialized."""

    def __init__(self, message: str = "Quantum simulator backend is unavailable.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="SIMULATOR_UNAVAILABLE",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details,
        )


class ResultAnalysisFailedException(BloopException):
    """Raised when post-simulation statistical analysis or metric calculation fails."""

    def __init__(self, message: str = "Simulation result analysis failed.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="RESULT_ANALYSIS_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class VisualizationDataInvalidException(BloopException):
    """Raised when visualization transformations encounter malformed distribution inputs."""

    def __init__(self, message: str = "Visualization data formatting failed.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="VISUALIZATION_DATA_INVALID",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class LaboratoryResourceLimitException(BloopException):
    """Raised when general quantum laboratory resource constraints are breached."""

    def __init__(self, message: str = "Laboratory resource limits exceeded.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="QUANTUM_RESOURCE_LIMIT",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )
