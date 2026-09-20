"""
Bloop Qiskit Aer Simulator Management
Provides configured AerSimulator instances with optional depolarization noise models and seed control.
"""

from typing import Optional


def get_aer_simulator(
    noise_level: float = 0.0,
    seed_simulator: Optional[int] = None,
):
    """
    Constructs an AerSimulator instance.
    Optionally applies a depolarizing noise model if noise_level > 0.
    """
    from qiskit_aer import AerSimulator

    noise_model = None
    if noise_level > 0.001:
        noise_model = build_depolarizing_noise_model(noise_level)

    sim_kwargs = {}
    if seed_simulator is not None:
        sim_kwargs["seed_simulator"] = seed_simulator

    if noise_model is not None:
        return AerSimulator(noise_model=noise_model, **sim_kwargs)
    return AerSimulator(**sim_kwargs)


def build_depolarizing_noise_model(noise_level: float):
    """Builds a 1-qubit and 2-qubit depolarizing noise model."""
    try:
        from qiskit_aer.noise import NoiseModel, depolarizing_error

        noise_model = NoiseModel()
        # 1-qubit depolarizing error for single qubit gates
        error_1q = depolarizing_error(min(noise_level, 0.5), 1)
        noise_model.add_all_qubit_quantum_error(
            error_1q, ["h", "x", "y", "z", "s", "t", "rx", "ry", "rz"]
        )

        # 2-qubit depolarizing error for entangling gates
        error_2q = depolarizing_error(min(noise_level * 2.0, 0.5), 2)
        noise_model.add_all_qubit_quantum_error(
            error_2q, ["cx", "cz", "swap"]
        )
        return noise_model
    except Exception:
        return None
