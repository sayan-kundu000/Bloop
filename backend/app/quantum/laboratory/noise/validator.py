"""
Bloop Noise Parameter Validator
Validates physical boundaries for simulated quantum noise channels.
Ensures probabilities fall in [0.0, 1.0] and thermal relaxation satisfies T2 <= 2*T1.
"""

from typing import Optional
from backend.app.quantum.laboratory.exceptions import (
    NoiseModelInvalidException,
    NoiseParameterInvalidException,
)
from backend.app.quantum.laboratory.models import NoiseModelType
from backend.app.quantum.laboratory.schemas import NoiseModelConfigSchema

SUPPORTED_NOISE_MODELS = {m.value for m in NoiseModelType}


class NoiseValidator:
    """Validates noise model parameters against physical and mathematical constraints."""

    @classmethod
    def validate(cls, config: NoiseModelConfigSchema) -> None:
        """Validates a NoiseModelConfigSchema."""
        clean_model = config.model.lower().strip()
        if clean_model not in SUPPORTED_NOISE_MODELS:
            raise NoiseModelInvalidException(
                f"Noise model '{config.model}' is not supported. Supported models: {sorted(SUPPORTED_NOISE_MODELS)}",
                details={"model": config.model, "supported": sorted(SUPPORTED_NOISE_MODELS)},
            )

        # Probability validation
        if config.probability is not None:
            if config.probability < 0.0 or config.probability > 1.0:
                raise NoiseParameterInvalidException(
                    f"Noise probability must be in [0.0, 1.0], got {config.probability}.",
                    details={"probability": config.probability},
                )

        # Thermal relaxation validation
        if clean_model == NoiseModelType.THERMAL_RELAXATION.value:
            t1 = config.t1 if config.t1 is not None else 50.0  # default 50 us
            t2 = config.t2 if config.t2 is not None else 70.0  # default 70 us

            if t1 <= 0.0:
                raise NoiseParameterInvalidException(
                    f"T1 relaxation time must be strictly positive, got {t1}.",
                    details={"t1": t1},
                )
            if t2 <= 0.0:
                raise NoiseParameterInvalidException(
                    f"T2 dephasing time must be strictly positive, got {t2}.",
                    details={"t2": t2},
                )
            # Physical requirement: T2 <= 2*T1
            if t2 > 2.0 * t1:
                raise NoiseParameterInvalidException(
                    f"Physical law violation: T2 ({t2} µs) cannot exceed 2*T1 ({2.0 * t1} µs).",
                    details={"t1": t1, "t2": t2, "max_allowable_t2": 2.0 * t1},
                )

        # Readout error probabilities
        if clean_model == NoiseModelType.READOUT_ERROR.value:
            p01 = config.p0_given_1 if config.p0_given_1 is not None else 0.02
            p10 = config.p1_given_0 if config.p1_given_0 is not None else 0.02
            if p01 < 0.0 or p01 > 1.0 or p10 < 0.0 or p10 > 1.0:
                raise NoiseParameterInvalidException(
                    f"Readout error probabilities must be in [0.0, 1.0], got p(0|1)={p01}, p(1|0)={p10}.",
                    details={"p0_given_1": p01, "p1_given_0": p10},
                )
