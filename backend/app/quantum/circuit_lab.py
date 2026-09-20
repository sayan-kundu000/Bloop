"""
Bloop Quantum Circuit Laboratory Engine
Legacy facade providing full backward compatibility for Prompt 22 interfaces,
delegating internally to the dedicated QuantumLaboratoryService (Prompt 26).
"""

from typing import Optional
from backend.app.quantum.laboratory.schemas import (
    CircuitLabRequestSchema,
    GateOperationSchema,
    NoiseModelConfigSchema,
)
from backend.app.quantum.laboratory.service import QuantumLaboratoryService
from backend.app.schemas.quantum import QuantumCircuitRequest, QuantumCircuitResponse


class QuantumCircuitLab:
    """
    Quantum Circuit Laboratory Engine.
    Enables arbitrary qubit and gate composition, ideal simulation,
    noisy hardware decoherence simulation, ASCII diagram generation, and OpenQASM export.
    """

    def __init__(self):
        self._service = QuantumLaboratoryService()

    def execute_circuit(self, req: QuantumCircuitRequest, user_id: Optional[int] = None) -> QuantumCircuitResponse:
        """Executes circuit request through the isolated laboratory pipeline."""
        gate_schemas = [
            GateOperationSchema(
                gate=op.gate,
                target=op.target,
                control=op.control,
                parameter=op.parameter,
            )
            for op in req.gates
        ]

        noise_cfg = None
        if req.noise:
            noise_cfg = NoiseModelConfigSchema(**req.noise)

        lab_req = CircuitLabRequestSchema(
            num_qubits=req.num_qubits,
            gates=gate_schemas,
            preset=req.preset,
            framework=req.framework or "qiskit",
            shots=req.shots,
            noise_level=req.noise_level,
            noise=noise_cfg,
            noise_profile=req.noise_profile,
            seed=req.seed,
        )

        res = self._service.execute_circuit(lab_req, user_id=user_id)

        return QuantumCircuitResponse(
            num_qubits=res.num_qubits,
            circuit_depth=res.circuit_depth,
            total_gates=res.total_gates,
            counts=res.counts,
            probabilities=res.probabilities,
            state_vector=res.state_vector,
            qasm=res.qasm,
            circuit_diagram_ascii=res.circuit_diagram_ascii,
            is_noisy_simulation=res.is_noisy_simulation,
            execution_time_ms=res.execution_time_ms,
            entropy=res.entropy,
            dominant_state=res.dominant_state,
            noise_model=res.noise_model,
            seed=res.seed,
            framework=res.framework,
            backend=res.backend,
        )
