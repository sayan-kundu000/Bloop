"""
Bloop Noise Profiles & Configuration
Defines standard configuration presets (IDEAL, LOW, MEDIUM, HIGH) representing
controlled simulated noise environments for educational and benchmarking experiments.
"""

from typing import Dict, List, Optional
from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError
from backend.app.quantum.laboratory.models import NoiseProfile
from backend.app.quantum.laboratory.schemas import NoiseModelConfigSchema, NoiseProfileInfoSchema
from backend.app.quantum.laboratory.noise.models import SINGLE_QUBIT_GATES, TWO_QUBIT_GATES

PROFILES: Dict[str, Dict] = {
    NoiseProfile.IDEAL.value: {
        "id": NoiseProfile.IDEAL.value,
        "name": "Ideal Simulation (Zero Noise)",
        "description": "Pure state unitary evolution without decoherence, gate imperfections, or readout errors.",
        "model": "ideal",
        "probability": 0.0,
        "readout_error": 0.0,
    },
    NoiseProfile.LOW_NOISE.value: {
        "id": NoiseProfile.LOW_NOISE.value,
        "name": "Low Noise Environment",
        "description": "Mild depolarizing noise (p=0.005 on 1Q, p=0.01 on 2Q) with minimal 1% readout measurement error.",
        "model": "depolarizing",
        "probability": 0.005,
        "readout_error": 0.01,
    },
    NoiseProfile.MEDIUM_NOISE.value: {
        "id": NoiseProfile.MEDIUM_NOISE.value,
        "name": "Medium Noise Environment",
        "description": "Typical near-term NISQ device abstraction with p=0.02 depolarizing noise and 3% readout error.",
        "model": "depolarizing",
        "probability": 0.02,
        "readout_error": 0.03,
    },
    NoiseProfile.HIGH_NOISE.value: {
        "id": NoiseProfile.HIGH_NOISE.value,
        "name": "High Noise Environment",
        "description": "Significant decoherence environment with p=0.06 depolarizing noise and 6% readout error.",
        "model": "depolarizing",
        "probability": 0.06,
        "readout_error": 0.06,
    },
}


class NoiseProfiles:
    """Catalog and builder for standard noise environment profiles."""

    @classmethod
    def list_profiles(cls) -> List[NoiseProfileInfoSchema]:
        """Returns metadata for all available preset profiles."""
        return [
            NoiseProfileInfoSchema(
                id=p["id"],
                name=p["name"],
                description=p["description"],
                model=p["model"],
                probability=p["probability"],
                readout_error=p["readout_error"],
            )
            for p in PROFILES.values()
        ]

    @classmethod
    def get_profile(cls, profile_name: str) -> Optional[Dict]:
        """Retrieves profile specification by name."""
        clean = profile_name.lower().strip()
        return PROFILES.get(clean)

    @classmethod
    def build_profile_model(cls, profile_name: str) -> Optional[NoiseModel]:
        """Builds a Qiskit Aer NoiseModel for a given preset profile."""
        clean = profile_name.lower().strip()
        if clean == NoiseProfile.IDEAL.value or clean not in PROFILES:
            return None

        p_info = PROFILES[clean]
        p_depol = p_info["probability"]
        p_readout = p_info["readout_error"]

        model = NoiseModel()
        if p_depol > 0.0:
            err_1q = depolarizing_error(p_depol, 1)
            err_2q = depolarizing_error(min(p_depol * 2.0, 0.5), 2)
            model.add_all_qubit_quantum_error(err_1q, SINGLE_QUBIT_GATES)
            model.add_all_qubit_quantum_error(err_2q, TWO_QUBIT_GATES)

        if p_readout > 0.0:
            ro_err = ReadoutError([
                [1.0 - p_readout, p_readout],
                [p_readout, 1.0 - p_readout],
            ])
            model.add_all_qubit_readout_error(ro_err)

        return model
