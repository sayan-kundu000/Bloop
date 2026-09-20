"""
Bloop Noise Model Factory
Constructs mathematically grounded Qiskit Aer NoiseModel instances for
depolarization, bit-flip, phase-flip, bit-phase-flip, thermal relaxation, and readout errors.
"""

from typing import List, Optional
from qiskit_aer.noise import (
    NoiseModel,
    depolarizing_error,
    pauli_error,
    thermal_relaxation_error,
    ReadoutError,
)
from backend.app.quantum.laboratory.models import NoiseModelType
from backend.app.quantum.laboratory.schemas import NoiseModelConfigSchema
from backend.app.quantum.laboratory.noise.validator import NoiseValidator

SINGLE_QUBIT_GATES = ["h", "x", "y", "z", "s", "t", "rx", "ry", "rz"]
TWO_QUBIT_GATES = ["cx", "cz", "swap"]


class NoiseModelFactory:
    """Creates Qiskit Aer NoiseModel instances from structured configurations."""

    @classmethod
    def build_from_config(cls, config: NoiseModelConfigSchema) -> Optional[NoiseModel]:
        """Validates configuration and builds the appropriate Aer NoiseModel."""
        NoiseValidator.validate(config)
        m = config.model.lower().strip()

        if m == NoiseModelType.DEPOLARIZING.value:
            prob = config.probability if config.probability is not None else 0.01
            return cls.build_depolarizing_model(prob)
        elif m == NoiseModelType.BIT_FLIP.value:
            prob = config.probability if config.probability is not None else 0.01
            return cls.build_bit_flip_model(prob)
        elif m == NoiseModelType.PHASE_FLIP.value:
            prob = config.probability if config.probability is not None else 0.01
            return cls.build_phase_flip_model(prob)
        elif m == NoiseModelType.BIT_PHASE_FLIP.value:
            prob = config.probability if config.probability is not None else 0.01
            return cls.build_bit_phase_flip_model(prob)
        elif m == NoiseModelType.THERMAL_RELAXATION.value:
            t1 = config.t1 if config.t1 is not None else 50.0
            t2 = config.t2 if config.t2 is not None else 70.0
            gate_time = config.gate_time if config.gate_time is not None else 0.1
            return cls.build_thermal_relaxation_model(t1=t1, t2=t2, gate_time=gate_time)
        elif m == NoiseModelType.READOUT_ERROR.value:
            p01 = config.p0_given_1 if config.p0_given_1 is not None else 0.02
            p10 = config.p1_given_0 if config.p1_given_0 is not None else 0.02
            return cls.build_readout_error_model(p0_given_1=p01, p1_given_0=p10)

        return None

    @classmethod
    def build_depolarizing_model(cls, probability: float) -> Optional[NoiseModel]:
        """Builds a depolarizing noise model for single- and two-qubit gates."""
        if probability <= 0.0001:
            return None
        model = NoiseModel()
        p_1q = min(probability, 0.5)
        p_2q = min(probability * 2.0, 0.75)

        err_1q = depolarizing_error(p_1q, 1)
        err_2q = depolarizing_error(p_2q, 2)

        model.add_all_qubit_quantum_error(err_1q, SINGLE_QUBIT_GATES)
        model.add_all_qubit_quantum_error(err_2q, TWO_QUBIT_GATES)
        return model

    @classmethod
    def build_bit_flip_model(cls, probability: float) -> Optional[NoiseModel]:
        """Pauli X bit-flip channel."""
        if probability <= 0.0001:
            return None
        model = NoiseModel()
        p = min(probability, 0.5)
        # Pauli-X bit flip error
        err_1q = pauli_error([("X", p), ("I", 1.0 - p)])
        # For 2-qubit gates, tensor independent bit flips
        err_2q = err_1q.tensor(err_1q)

        model.add_all_qubit_quantum_error(err_1q, SINGLE_QUBIT_GATES)
        model.add_all_qubit_quantum_error(err_2q, TWO_QUBIT_GATES)
        return model

    @classmethod
    def build_phase_flip_model(cls, probability: float) -> Optional[NoiseModel]:
        """Pauli Z phase-flip channel."""
        if probability <= 0.0001:
            return None
        model = NoiseModel()
        p = min(probability, 0.5)
        err_1q = pauli_error([("Z", p), ("I", 1.0 - p)])
        err_2q = err_1q.tensor(err_1q)

        model.add_all_qubit_quantum_error(err_1q, SINGLE_QUBIT_GATES)
        model.add_all_qubit_quantum_error(err_2q, TWO_QUBIT_GATES)
        return model

    @classmethod
    def build_bit_phase_flip_model(cls, probability: float) -> Optional[NoiseModel]:
        """Pauli Y bit-phase-flip channel."""
        if probability <= 0.0001:
            return None
        model = NoiseModel()
        p = min(probability, 0.5)
        err_1q = pauli_error([("Y", p), ("I", 1.0 - p)])
        err_2q = err_1q.tensor(err_1q)

        model.add_all_qubit_quantum_error(err_1q, SINGLE_QUBIT_GATES)
        model.add_all_qubit_quantum_error(err_2q, TWO_QUBIT_GATES)
        return model

    @classmethod
    def build_thermal_relaxation_model(
        cls,
        t1: float = 50.0,
        t2: float = 70.0,
        gate_time: float = 0.1,
    ) -> Optional[NoiseModel]:
        """Thermal relaxation (T1) and dephasing (T2) decoherence model."""
        model = NoiseModel()
        # 1-qubit gate relaxation
        err_1q = thermal_relaxation_error(t1=t1, t2=t2, time=gate_time)
        # 2-qubit gate relaxation takes ~2x gate duration
        err_2q = thermal_relaxation_error(t1=t1, t2=t2, time=gate_time * 2.0).tensor(
            thermal_relaxation_error(t1=t1, t2=t2, time=gate_time * 2.0)
        )

        model.add_all_qubit_quantum_error(err_1q, SINGLE_QUBIT_GATES)
        model.add_all_qubit_quantum_error(err_2q, TWO_QUBIT_GATES)
        return model

    @classmethod
    def build_readout_error_model(
        cls,
        p0_given_1: float = 0.02,
        p1_given_0: float = 0.02,
    ) -> Optional[NoiseModel]:
        """Measurement readout confusion error model."""
        model = NoiseModel()
        matrix = [
            [1.0 - p1_given_0, p1_given_0],
            [p0_given_1, 1.0 - p0_given_1],
        ]
        readout_err = ReadoutError(matrix)
        model.add_all_qubit_readout_error(readout_err)
        return model
