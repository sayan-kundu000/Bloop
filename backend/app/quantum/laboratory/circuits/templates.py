"""
Bloop Circuit Templates
Provides standard, deterministic benchmark and educational circuit configurations
along with theoretical analytical expectations.
"""

import math
from typing import Dict, List, Optional
from backend.app.quantum.laboratory.schemas import GateOperationSchema, TemplateInfoSchema


TEMPLATES: Dict[str, Dict] = {
    "bell_state": {
        "id": "bell_state",
        "name": "Bell State (|Φ⁺⟩)",
        "description": "Maximally entangled two-qubit Bell state |Φ⁺⟩ = (|00⟩ + |11⟩) / √2.",
        "qubits": 2,
        "gates": [
            GateOperationSchema(gate="h", target=0),
            GateOperationSchema(gate="cx", control=0, target=1),
        ],
        "expected_support": ["00", "11"],
        "analytical_probabilities": {"00": 0.5, "11": 0.5},
    },
    "ghz_state": {
        "id": "ghz_state",
        "name": "Greenberger-Horne-Zeilinger (GHZ) State",
        "description": "Tripartite entangled state |GHZ⟩ = (|000⟩ + |111⟩) / √2 across 3 qubits.",
        "qubits": 3,
        "gates": [
            GateOperationSchema(gate="h", target=0),
            GateOperationSchema(gate="cx", control=0, target=1),
            GateOperationSchema(gate="cx", control=1, target=2),
        ],
        "expected_support": ["000", "111"],
        "analytical_probabilities": {"000": 0.5, "111": 0.5},
    },
    "hadamard_superposition": {
        "id": "hadamard_superposition",
        "name": "Single-Qubit Hadamard Superposition",
        "description": "Places a single qubit in balanced superposition |+⟩ = (|0⟩ + |1⟩) / √2.",
        "qubits": 1,
        "gates": [
            GateOperationSchema(gate="h", target=0),
        ],
        "expected_support": ["0", "1"],
        "analytical_probabilities": {"0": 0.5, "1": 0.5},
    },
    "single_qubit_x": {
        "id": "single_qubit_x",
        "name": "Single-Qubit Bit-Flip (|1⟩)",
        "description": "Applies a Pauli-X gate to flip |0⟩ to |1⟩.",
        "qubits": 1,
        "gates": [
            GateOperationSchema(gate="x", target=0),
        ],
        "expected_support": ["1"],
        "analytical_probabilities": {"1": 1.0},
    },
    "superposition_4q": {
        "id": "superposition_4q",
        "name": "4-Qubit Equal Superposition Register",
        "description": "Applies Hadamard transforms to 4 qubits to generate equal support across all 16 computational basis states.",
        "qubits": 4,
        "gates": [
            GateOperationSchema(gate="h", target=0),
            GateOperationSchema(gate="h", target=1),
            GateOperationSchema(gate="h", target=2),
            GateOperationSchema(gate="h", target=3),
        ],
        "expected_support": [format(i, "04b") for i in range(16)],
        "analytical_probabilities": {format(i, "04b"): 1.0 / 16.0 for i in range(16)},
    },
    "rotation_experiment": {
        "id": "rotation_experiment",
        "name": "Parameterized Rotation Interference",
        "description": "Demonstrates quantum phase interference using H and Ry(π/3) gates.",
        "qubits": 1,
        "gates": [
            GateOperationSchema(gate="h", target=0),
            GateOperationSchema(gate="ry", target=0, parameter=math.pi / 3.0),
            GateOperationSchema(gate="h", target=0),
        ],
        "expected_support": ["0", "1"],
        "analytical_probabilities": {"0": 0.75, "1": 0.25},
    },
    "entanglement_experiment": {
        "id": "entanglement_experiment",
        "name": "Two-Qubit Entanglement & Phase Shift",
        "description": "Creates entanglement followed by local Rz rotation for parity analysis.",
        "qubits": 2,
        "gates": [
            GateOperationSchema(gate="h", target=0),
            GateOperationSchema(gate="cx", control=0, target=1),
            GateOperationSchema(gate="rz", target=1, parameter=math.pi / 4.0),
        ],
        "expected_support": ["00", "11"],
        "analytical_probabilities": {"00": 0.5, "11": 0.5},
    },
}


class CircuitTemplates:
    """Catalog and resolver for pre-defined circuit templates."""

    @classmethod
    def list_templates(cls) -> List[TemplateInfoSchema]:
        """Returns metadata for all available templates."""
        results = []
        for tid, data in TEMPLATES.items():
            results.append(
                TemplateInfoSchema(
                    id=data["id"],
                    name=data["name"],
                    description=data["description"],
                    qubits=data["qubits"],
                    depth=len(data["gates"]),
                    gate_count=len(data["gates"]),
                    gates=data["gates"],
                    expected_support=data["expected_support"],
                )
            )
        return results

    @classmethod
    def get_template(cls, template_id: str) -> Optional[Dict]:
        """Retrieves template by ID (case-insensitive)."""
        clean_id = template_id.lower().strip()
        # Aliases
        if clean_id in ("bell", "bell_state"):
            clean_id = "bell_state"
        elif clean_id in ("ghz", "ghz_state"):
            clean_id = "ghz_state"
        elif clean_id in ("h", "single_qubit_h", "hadamard", "superposition"):
            clean_id = "hadamard_superposition"
        elif clean_id in ("x", "single_qubit_x", "not", "bit_flip"):
            clean_id = "single_qubit_x"
        elif clean_id in ("superposition_4", "superposition_4q"):
            clean_id = "superposition_4q"
        elif clean_id in ("rotation", "rotation_experiment"):
            clean_id = "rotation_experiment"
        elif clean_id in ("entanglement", "entanglement_experiment"):
            clean_id = "entanglement_experiment"

        return TEMPLATES.get(clean_id)
