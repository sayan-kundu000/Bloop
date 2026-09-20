"""
Bloop Laboratory Circuit Visualization Formatter
Generates ASCII circuit wire diagrams and structured timeline metadata for frontend rendering.
"""

from typing import Any, Dict, List
from qiskit import QuantumCircuit
from backend.app.quantum.laboratory.models import GateDefinition


class CircuitVisualizer:
    """Transforms QuantumCircuit structures into visualization-ready payloads."""

    @classmethod
    def render_ascii(cls, qc: QuantumCircuit) -> str:
        """Renders formatted ASCII representation of circuit wires."""
        try:
            return str(qc.draw(output="text"))
        except Exception:
            return f"QuantumCircuit({qc.num_qubits} qubits, {sum(qc.count_ops().values())} gates)"

    @classmethod
    def to_structured_timeline(
        cls,
        num_qubits: int,
        operations: List[GateDefinition],
    ) -> Dict[str, Any]:
        """
        Creates structured wire timeline data for interactive canvas/SVG rendering.
        Each wire contains an ordered list of gate slots.
        """
        wires: Dict[int, List[Dict[str, Any]]] = {q: [] for q in range(num_qubits)}

        for idx, op in enumerate(operations):
            gate_data = {
                "step": idx,
                "gate": op.gate.upper(),
                "target": op.target,
                "control": op.control,
                "parameter": round(op.parameter, 3) if op.parameter is not None else None,
            }
            wires[op.target].append(gate_data)
            if op.control is not None and op.control in wires:
                wires[op.control].append({
                    "step": idx,
                    "gate": "CTRL",
                    "target": op.target,
                    "control": op.control,
                    "parameter": None,
                })

        return {
            "num_qubits": num_qubits,
            "total_steps": len(operations),
            "wires": wires,
        }
