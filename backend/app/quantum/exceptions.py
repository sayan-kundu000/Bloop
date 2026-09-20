"""
Bloop Quantum Subsystem Exceptions
Provides domain-level exceptions specific to the quantum computing and hybrid ML layer.
Directly aligns with Bloop's standardized error code taxonomy.
"""

from backend.app.core.exceptions import (
    ErrorCode,
    QuantumDisabledException,
    QuantumUnavailableException,
    InvalidQuantumRequestException,
    QubitLimitExceededException,
    ShotLimitExceededException,
    QuantumExecutionTimeoutException,
    UnsupportedFrameworkException,
    UnsupportedExperimentException,
    HybridExecutionFailedException,
    QuantumExecutionError,
)

__all__ = [
    "ErrorCode",
    "QuantumDisabledException",
    "QuantumUnavailableException",
    "InvalidQuantumRequestException",
    "QubitLimitExceededException",
    "ShotLimitExceededException",
    "QuantumExecutionTimeoutException",
    "UnsupportedFrameworkException",
    "UnsupportedExperimentException",
    "HybridExecutionFailedException",
    "QuantumExecutionError",
]
