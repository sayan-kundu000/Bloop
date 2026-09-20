"""
Bloop Quantum Circuit & Noise Laboratory Service
Central orchestrator for Mode A (Ideal), Mode B (Noisy), Mode C (Comparison),
and Mode D (Robustness Parameter Sweeps).
Decoupled from core TTS, simulator-first, and enforces multi-tenant ownership.
"""

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from backend.app.core.logging import logger
from backend.app.quantum.config import quantum_config
from backend.app.quantum.laboratory.analysis.distributions import DistributionComparator
from backend.app.quantum.laboratory.analysis.measurements import MeasurementAnalyzer
from backend.app.quantum.laboratory.analysis.robustness import RobustnessAnalyzer
from backend.app.quantum.laboratory.circuits.builder import SafeCircuitBuilder
from backend.app.quantum.laboratory.circuits.templates import CircuitTemplates
from backend.app.quantum.laboratory.circuits.validator import CircuitValidator
from backend.app.quantum.laboratory.exceptions import (
    CircuitInvalidException,
    LaboratoryResourceLimitException,
)
from backend.app.quantum.laboratory.execution.executor import LaboratoryExecutor
from backend.app.quantum.laboratory.models import SupportedGate
from backend.app.quantum.laboratory.noise.configuration import NoiseProfiles
from backend.app.quantum.laboratory.noise.models import NoiseModelFactory
from backend.app.quantum.laboratory.schemas import (
    CircuitComparisonRequestSchema,
    CircuitComparisonResponseSchema,
    CircuitLabRequestSchema,
    CircuitLabResponseSchema,
    CircuitRobustnessRequestSchema,
    CircuitRobustnessResponseSchema,
    GateOperationSchema,
    NoiseProfileInfoSchema,
    RobustnessPointSchema,
    StateComparisonEntry,
    TemplateInfoSchema,
)
from backend.app.repositories.quantum_repository import QuantumRepository


class QuantumLaboratoryService:
    """Service orchestrating bounded circuit execution, noise modeling, and experiments."""

    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self.repo = QuantumRepository(db) if db is not None else None
        self.executor = LaboratoryExecutor()
        self.robustness_analyzer = RobustnessAnalyzer(self.executor)

    def _resolve_circuit_gates(
        self,
        num_qubits: int,
        preset: Optional[str],
        gates: List[GateOperationSchema],
    ) -> tuple[int, List[GateOperationSchema]]:
        """Resolves either a pre-defined template or custom gate sequence."""
        if preset:
            tmpl = CircuitTemplates.get_template(preset)
            if tmpl:
                q_count = tmpl["qubits"]
                gate_ops = tmpl["gates"]
                return q_count, gate_ops
        return num_qubits, gates

    def execute_circuit(
        self,
        req: CircuitLabRequestSchema,
        user_id: Optional[int] = None,
    ) -> CircuitLabResponseSchema:
        """
        Mode A & Mode B: Executes a quantum circuit under ideal or noisy simulation.
        """
        # Resolve preset if provided
        q_count, raw_gates = self._resolve_circuit_gates(req.num_qubits, req.preset, req.gates)

        # Validate gate operations
        validated_ops = CircuitValidator.validate_operations(q_count, raw_gates)

        # Build Qiskit circuit
        qc, depth, total_gates = SafeCircuitBuilder.build(q_count, validated_ops, add_measurements=True)

        # Resolve noise model
        noise_model = None
        noise_model_desc = None
        is_noisy = False

        if req.noise_profile and req.noise_profile.lower() != "ideal":
            noise_model = NoiseProfiles.build_profile_model(req.noise_profile)
            noise_model_desc = f"profile:{req.noise_profile}"
            is_noisy = noise_model is not None
        elif req.noise is not None:
            noise_model = NoiseModelFactory.build_from_config(req.noise)
            noise_model_desc = req.noise.model
            is_noisy = noise_model is not None
        elif req.noise_level > 0.001:
            noise_model = NoiseModelFactory.build_depolarizing_model(req.noise_level)
            noise_model_desc = f"depolarizing(p={req.noise_level})"
            is_noisy = noise_model is not None

        # Execute simulation
        if is_noisy and noise_model is not None:
            counts, exec_ms = self.executor.execute_noisy(
                circuit=qc,
                noise_model=noise_model,
                shots=req.shots,
                seed=req.seed,
            )
            state_vec = None
        else:
            counts, state_vec, exec_ms = self.executor.execute_ideal(
                circuit=qc,
                shots=req.shots,
                seed=req.seed,
                extract_statevector=True,
            )

        summary = MeasurementAnalyzer.summarize(counts, req.shots)
        ascii_diag = SafeCircuitBuilder.generate_ascii_diagram(qc)
        qasm_str = SafeCircuitBuilder.export_qasm(qc)

        response = CircuitLabResponseSchema(
            num_qubits=q_count,
            circuit_depth=depth,
            total_gates=total_gates,
            counts=counts,
            probabilities=summary.probabilities,
            state_vector=state_vec,
            qasm=qasm_str,
            circuit_diagram_ascii=ascii_diag,
            is_noisy_simulation=is_noisy,
            noise_model=noise_model_desc,
            execution_time_ms=exec_ms,
            entropy=summary.entropy,
            dominant_state=summary.dominant_state,
            seed=req.seed,
            framework="qiskit",
            backend="aer_simulator",
        )

        # Multi-tenant persistence
        self._safe_persist(
            experiment_type="basic_circuit",
            title=f"Circuit Simulation ({q_count}Q, {total_gates} gates, {'noisy' if is_noisy else 'ideal'})",
            input_payload=req.model_dump(),
            results=response.model_dump(),
            user_id=user_id,
            qubit_count=q_count,
            circuit_depth=depth,
            execution_time_ms=exec_ms,
        )

        return response

    def compare_circuits(
        self,
        req: CircuitComparisonRequestSchema,
        user_id: Optional[int] = None,
    ) -> CircuitComparisonResponseSchema:
        """
        Mode C: Comparative Experiment between ideal and noisy execution.
        """
        q_count, raw_gates = self._resolve_circuit_gates(req.num_qubits, req.preset, req.gates)
        validated_ops = CircuitValidator.validate_operations(q_count, raw_gates)
        qc, depth, total_gates = SafeCircuitBuilder.build(q_count, validated_ops, add_measurements=True)

        # Resolve noise model
        noise_model = None
        noise_desc = req.noise_profile or "medium_noise"
        if req.noise_profile:
            noise_model = NoiseProfiles.build_profile_model(req.noise_profile)
        elif req.noise:
            noise_model = NoiseModelFactory.build_from_config(req.noise)
            noise_desc = req.noise.model

        if noise_model is None:
            noise_model = NoiseProfiles.build_profile_model("medium_noise")
            noise_desc = "medium_noise"

        # Execute Ideal
        ideal_counts, _, ideal_ms = self.executor.execute_ideal(
            circuit=qc,
            shots=req.shots,
            seed=req.seed,
            extract_statevector=False,
        )

        # Execute Noisy
        noisy_counts, noisy_ms = self.executor.execute_noisy(
            circuit=qc,
            noise_model=noise_model,
            shots=req.shots,
            seed=req.seed,
        )

        # Compare distributions
        comp_res = DistributionComparator.compare(
            ideal_counts=ideal_counts,
            noisy_counts=noisy_counts,
            shots_ideal=req.shots,
            shots_noisy=req.shots,
        )

        p_ideal = MeasurementAnalyzer.normalize_counts(ideal_counts, req.shots)
        p_noisy = MeasurementAnalyzer.normalize_counts(noisy_counts, req.shots)
        ascii_diag = SafeCircuitBuilder.generate_ascii_diagram(qc)

        entries = [
            StateComparisonEntry(
                state=item["state"],
                ideal_count=item["ideal_count"],
                noisy_count=item["noisy_count"],
                ideal_probability=item["ideal_probability"],
                noisy_probability=item["noisy_probability"],
                divergence=item["divergence"],
            )
            for item in comp_res.states_comparison
        ]

        total_exec_ms = round(ideal_ms + noisy_ms, 2)

        response = CircuitComparisonResponseSchema(
            num_qubits=q_count,
            circuit_depth=depth,
            total_gates=total_gates,
            ideal_counts=ideal_counts,
            noisy_counts=noisy_counts,
            ideal_probabilities=p_ideal,
            noisy_probabilities=p_noisy,
            total_variation_distance=comp_res.total_variation_distance,
            classical_fidelity=comp_res.classical_fidelity,
            ideal_entropy=comp_res.ideal_entropy,
            noisy_entropy=comp_res.noisy_entropy,
            max_divergence=comp_res.max_divergence,
            dominant_ideal_state=comp_res.dominant_ideal_state,
            dominant_noisy_state=comp_res.dominant_noisy_state,
            states_comparison=entries,
            circuit_diagram_ascii=ascii_diag,
            noise_model=noise_desc,
            execution_time_ms=total_exec_ms,
        )

        self._safe_persist(
            experiment_type="basic_circuit",
            title=f"Ideal vs Noisy Comparison ({q_count}Q, TVD={comp_res.total_variation_distance})",
            input_payload=req.model_dump(),
            results=response.model_dump(),
            user_id=user_id,
            qubit_count=q_count,
            circuit_depth=depth,
            execution_time_ms=total_exec_ms,
        )

        return response

    def run_robustness(
        self,
        req: CircuitRobustnessRequestSchema,
        user_id: Optional[int] = None,
    ) -> CircuitRobustnessResponseSchema:
        """
        Mode D: Robustness Experiment across a bounded parameter sweep.
        """
        q_count, raw_gates = self._resolve_circuit_gates(req.num_qubits, req.preset, req.gates)
        validated_ops = CircuitValidator.validate_operations(q_count, raw_gates)
        qc, depth, total_gates = SafeCircuitBuilder.build(q_count, validated_ops, add_measurements=True)

        sweep_res = self.robustness_analyzer.run_sweep(
            circuit=qc,
            noise_model_type=req.noise_model,
            sweep_config=req.sweep,
            shots=req.shots,
            repeats_per_point=req.repeats_per_point,
            target_state=req.target_state,
            base_seed=req.seed,
        )

        point_schemas = [
            RobustnessPointSchema(
                parameter_value=pt.parameter_value,
                mean_fidelity=pt.mean_fidelity,
                std_fidelity=pt.std_fidelity,
                mean_tvd=pt.mean_tvd,
                std_tvd=pt.std_tvd,
                success_probability=pt.success_probability,
                execution_time_ms=pt.execution_time_ms,
                repetition_count=pt.repetition_count,
            )
            for pt in sweep_res.points
        ]

        response = CircuitRobustnessResponseSchema(
            sweep_parameter=sweep_res.sweep_parameter,
            points=point_schemas,
            target_state=sweep_res.target_state,
            baseline_ideal_state=sweep_res.target_state or "",
            circuit_depth=depth,
            total_gates=total_gates,
            total_runs=sweep_res.total_runs,
            total_execution_time_ms=sweep_res.total_execution_time_ms,
            summary=sweep_res.summary,
        )

        self._safe_persist(
            experiment_type="basic_circuit",
            title=f"Robustness Sweep ({q_count}Q, {req.noise_model}, {len(point_schemas)} points)",
            input_payload=req.model_dump(),
            results=response.model_dump(),
            user_id=user_id,
            qubit_count=q_count,
            circuit_depth=depth,
            execution_time_ms=sweep_res.total_execution_time_ms,
        )

        return response

    @classmethod
    def list_templates(cls) -> List[TemplateInfoSchema]:
        """Returns metadata for deterministic templates."""
        return CircuitTemplates.list_templates()

    @classmethod
    def list_noise_profiles(cls) -> List[NoiseProfileInfoSchema]:
        """Returns available preset noise profiles."""
        return NoiseProfiles.list_profiles()

    @classmethod
    def get_supported_gates(cls) -> List[Dict[str, Any]]:
        """Returns the approved gate whitelist and specifications."""
        return [
            {"gate": "h", "type": "single_qubit", "description": "Hadamard superposition gate"},
            {"gate": "x", "type": "single_qubit", "description": "Pauli-X bit-flip gate"},
            {"gate": "y", "type": "single_qubit", "description": "Pauli-Y bit-and-phase flip gate"},
            {"gate": "z", "type": "single_qubit", "description": "Pauli-Z phase-flip gate"},
            {"gate": "s", "type": "single_qubit", "description": "S phase gate (π/2 phase)"},
            {"gate": "t", "type": "single_qubit", "description": "T phase gate (π/4 phase)"},
            {"gate": "rx", "type": "parameterized", "description": "X-axis rotation by angle θ"},
            {"gate": "ry", "type": "parameterized", "description": "Y-axis rotation by angle θ"},
            {"gate": "rz", "type": "parameterized", "description": "Z-axis rotation by angle θ"},
            {"gate": "cx", "type": "two_qubit", "description": "Controlled-NOT (CNOT) entangling gate"},
            {"gate": "cz", "type": "two_qubit", "description": "Controlled-Z phase entangling gate"},
            {"gate": "swap", "type": "two_qubit", "description": "SWAP state exchange gate"},
        ]

    def _safe_persist(
        self,
        experiment_type: str,
        title: str,
        input_payload: Dict[str, Any],
        results: Dict[str, Any],
        user_id: Optional[int] = None,
        qubit_count: int = 2,
        circuit_depth: int = 1,
        execution_time_ms: float = 0.0,
    ) -> None:
        """Multi-tenant experiment persistence guard."""
        if not self.repo or user_id is None:
            return
        try:
            self.repo.create(
                user_id=user_id,
                experiment_type=experiment_type,
                title=title,
                description="Bloop Quantum Circuit & Noise Laboratory Experiment",
                qubit_count=qubit_count,
                circuit_depth=circuit_depth,
                execution_time_ms=execution_time_ms,
                simulator="aer_simulator",
                input_payload=input_payload,
                results=results,
            )
        except Exception as e:
            logger.warning(f"Failed to persist quantum laboratory experiment: {e}")
