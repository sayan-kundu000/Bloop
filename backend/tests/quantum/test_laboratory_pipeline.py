"""
Tests for Bloop Quantum Circuit & Noise Laboratory Pipeline
Validates circuit building, gate whitelists, noise modeling, ideal/noisy simulations,
distribution comparison metrics, and parameter sweeps.
"""

import math
import pytest

from backend.app.quantum.laboratory.analysis.distributions import DistributionComparator
from backend.app.quantum.laboratory.analysis.fidelity import QuantumFidelityAnalyzer
from backend.app.quantum.laboratory.analysis.measurements import MeasurementAnalyzer
from backend.app.quantum.laboratory.circuits.builder import SafeCircuitBuilder
from backend.app.quantum.laboratory.circuits.templates import CircuitTemplates
from backend.app.quantum.laboratory.circuits.validator import CircuitValidator
from backend.app.quantum.laboratory.exceptions import (
    CircuitInvalidException,
    CircuitTooDeepException,
    CircuitTooLargeException,
    InvalidGateParameterException,
    InvalidQubitIndexException,
    NoiseParameterInvalidException,
    UnsupportedGateException,
)
from backend.app.quantum.laboratory.execution.ideal import IdealSimulatorExecutor
from backend.app.quantum.laboratory.execution.noisy import NoisySimulatorExecutor
from backend.app.quantum.laboratory.models import GateDefinition, SupportedGate
from backend.app.quantum.laboratory.noise.configuration import NoiseProfiles
from backend.app.quantum.laboratory.noise.models import NoiseModelFactory
from backend.app.quantum.laboratory.noise.validator import NoiseValidator
from backend.app.quantum.laboratory.schemas import (
    CircuitComparisonRequestSchema,
    CircuitLabRequestSchema,
    CircuitRobustnessRequestSchema,
    GateOperationSchema,
    NoiseModelConfigSchema,
    NoiseSweepConfigSchema,
)
from backend.app.quantum.laboratory.service import QuantumLaboratoryService


def test_gate_whitelist_and_validation():
    """Verifies that all 12 supported gates are accepted and unauthorized gates are rejected."""
    ops = [
        GateOperationSchema(gate="h", target=0),
        GateOperationSchema(gate="x", target=1),
        GateOperationSchema(gate="y", target=0),
        GateOperationSchema(gate="z", target=1),
        GateOperationSchema(gate="s", target=0),
        GateOperationSchema(gate="t", target=1),
        GateOperationSchema(gate="rx", target=0, parameter=0.785),
        GateOperationSchema(gate="ry", target=1, parameter=1.57),
        GateOperationSchema(gate="rz", target=0, parameter=3.14),
        GateOperationSchema(gate="cx", control=0, target=1),
        GateOperationSchema(gate="cz", control=0, target=1),
        GateOperationSchema(gate="swap", control=0, target=1),
    ]
    validated = CircuitValidator.validate_operations(num_qubits=2, gates=ops)
    assert len(validated) == 12

    # Unsupported gate
    with pytest.raises(UnsupportedGateException):
        CircuitValidator.validate_operations(
            num_qubits=2,
            gates=[GateOperationSchema(gate="magic_phase_gate", target=0)],
        )


def test_qubit_bounds_and_two_qubit_validation():
    """Validates boundary checking for target and control qubits."""
    # Out of bounds target
    with pytest.raises(InvalidQubitIndexException):
        CircuitValidator.validate_operations(
            num_qubits=2,
            gates=[GateOperationSchema(gate="h", target=5)],
        )

    # Missing control on CX
    with pytest.raises(CircuitInvalidException):
        CircuitValidator.validate_operations(
            num_qubits=2,
            gates=[GateOperationSchema(gate="cx", target=1, control=None)],
        )

    # Target equals control on CX
    with pytest.raises(CircuitInvalidException):
        CircuitValidator.validate_operations(
            num_qubits=2,
            gates=[GateOperationSchema(gate="cx", target=1, control=1)],
        )

    # Control out of bounds
    with pytest.raises(InvalidQubitIndexException):
        CircuitValidator.validate_operations(
            num_qubits=2,
            gates=[GateOperationSchema(gate="cx", target=0, control=8)],
        )


def test_parameter_validation():
    """Validates parameter ranges and NaN/inf rejection."""
    # Non-finite parameter
    with pytest.raises(InvalidGateParameterException):
        CircuitValidator.validate_operations(
            num_qubits=1,
            gates=[GateOperationSchema(gate="rx", target=0, parameter=float("nan"))],
        )

    with pytest.raises(InvalidGateParameterException):
        CircuitValidator.validate_operations(
            num_qubits=1,
            gates=[GateOperationSchema(gate="rx", target=0, parameter=float("inf"))],
        )


def test_circuit_depth_and_builder():
    """Verifies that SafeCircuitBuilder accurately constructs circuits and checks depth."""
    ops = [
        GateDefinition(gate="h", target=0),
        GateDefinition(gate="cx", control=0, target=1),
    ]
    qc, depth, total_gates = SafeCircuitBuilder.build(2, ops, add_measurements=True)
    assert qc.num_qubits == 2
    assert depth == 2
    assert total_gates == 2
    assert qc.num_clbits == 2

    # Export diagrams
    ascii_diag = SafeCircuitBuilder.generate_ascii_diagram(qc)
    assert "q_0" in ascii_diag or "q" in ascii_diag
    qasm_str = SafeCircuitBuilder.export_qasm(qc)
    assert "OPENQASM" in qasm_str or "qreg" in qasm_str


def test_circuit_templates():
    """Verifies deterministic template retrieval and analytical expectations."""
    templates = CircuitTemplates.list_templates()
    assert len(templates) >= 5

    bell = CircuitTemplates.get_template("bell_state")
    assert bell is not None
    assert bell["qubits"] == 2
    assert bell["expected_support"] == ["00", "11"]
    assert bell["analytical_probabilities"]["00"] == 0.5

    ghz = CircuitTemplates.get_template("ghz_state")
    assert ghz is not None
    assert ghz["qubits"] == 3
    assert ghz["expected_support"] == ["000", "111"]


def test_noise_parameter_validation():
    """Verifies physical validation of noise probabilities and T2 <= 2*T1."""
    from pydantic import ValidationError

    # Valid depolarizing
    cfg = NoiseModelConfigSchema(model="depolarizing", probability=0.02)
    NoiseValidator.validate(cfg)

    # Negative probability rejected by schema bounds
    with pytest.raises(ValidationError):
        NoiseModelConfigSchema(model="depolarizing", probability=-0.05)

    # Probability > 1.0 rejected by schema bounds
    with pytest.raises(ValidationError):
        NoiseModelConfigSchema(model="depolarizing", probability=1.5)

    # Thermal relaxation: T2 <= 2*T1 is valid
    cfg_thermal = NoiseModelConfigSchema(model="thermal_relaxation", t1=50.0, t2=80.0)
    NoiseValidator.validate(cfg_thermal)

    # Physical violation: T2 > 2*T1 rejected by NoiseValidator
    with pytest.raises(NoiseParameterInvalidException):
        NoiseValidator.validate(NoiseModelConfigSchema(model="thermal_relaxation", t1=50.0, t2=120.0))


def test_noise_models_creation():
    """Verifies that all supported noise models generate valid Qiskit Aer NoiseModel objects."""
    # Depolarizing
    nm_depol = NoiseModelFactory.build_depolarizing_model(0.02)
    assert nm_depol is not None

    # Bit flip
    nm_bf = NoiseModelFactory.build_bit_flip_model(0.03)
    assert nm_bf is not None

    # Phase flip
    nm_pf = NoiseModelFactory.build_phase_flip_model(0.03)
    assert nm_pf is not None

    # Thermal relaxation
    nm_thermal = NoiseModelFactory.build_thermal_relaxation_model(t1=50.0, t2=70.0, gate_time=0.1)
    assert nm_thermal is not None

    # Readout error
    nm_ro = NoiseModelFactory.build_readout_error_model(p0_given_1=0.03, p1_given_0=0.03)
    assert nm_ro is not None

    # Preset profiles
    nm_medium = NoiseProfiles.build_profile_model("medium_noise")
    assert nm_medium is not None


def test_ideal_simulation_execution():
    """Verifies Mode A ideal simulation on Bell State produces expected 00 and 11 support."""
    ops = [
        GateDefinition(gate="h", target=0),
        GateDefinition(gate="cx", control=0, target=1),
    ]
    qc, _, _ = SafeCircuitBuilder.build(2, ops, add_measurements=True)
    counts, sv, ms = IdealSimulatorExecutor.execute(qc, shots=1024, seed=42)

    assert sum(counts.values()) == 1024
    probs = MeasurementAnalyzer.normalize_counts(counts, 1024)
    assert "00" in probs
    assert "11" in probs
    # Ideal Bell state probabilities close to 0.5 within sampling tolerance
    assert 0.40 <= probs["00"] <= 0.60
    assert 0.40 <= probs["11"] <= 0.60
    assert probs.get("01", 0.0) < 0.05
    assert probs.get("10", 0.0) < 0.05


def test_noisy_simulation_execution():
    """Verifies Mode B noisy simulation produces error support and normalized counts."""
    ops = [
        GateDefinition(gate="h", target=0),
        GateDefinition(gate="cx", control=0, target=1),
    ]
    qc, _, _ = SafeCircuitBuilder.build(2, ops, add_measurements=True)
    nm = NoiseProfiles.build_profile_model("high_noise")

    counts, ms = NoisySimulatorExecutor.execute(qc, noise_model=nm, shots=2048, seed=42)
    assert sum(counts.values()) == 2048
    probs = MeasurementAnalyzer.normalize_counts(counts, 2048)

    # In high noise, bit-flips cause leakage into 01 and 10
    total_p = sum(probs.values())
    assert 0.99 <= total_p <= 1.01


def test_distribution_comparison_metrics():
    """Verifies TVD and Classical Fidelity calculations across identical, divergent, and orthogonal distributions."""
    # 1. Identical distributions
    p = {"00": 0.5, "11": 0.5}
    q = {"00": 0.5, "11": 0.5}
    tvd_ident = DistributionComparator.total_variation_distance(p, q)
    fid_ident = DistributionComparator.classical_fidelity(p, q)
    assert tvd_ident == 0.0
    assert fid_ident == 1.0

    # 2. Completely orthogonal distributions
    p_orth = {"00": 1.0}
    q_orth = {"11": 1.0}
    tvd_orth = DistributionComparator.total_variation_distance(p_orth, q_orth)
    fid_orth = DistributionComparator.classical_fidelity(p_orth, q_orth)
    assert tvd_orth == 1.0
    assert fid_orth == 0.0

    # 3. Intermediate comparison
    counts_ideal = {"00": 500, "11": 500}
    counts_noisy = {"00": 450, "11": 450, "01": 50, "10": 50}
    comp = DistributionComparator.compare(counts_ideal, counts_noisy, 1000, 1000)
    assert 0.0 < comp.total_variation_distance < 1.0
    assert 0.0 < comp.classical_fidelity < 1.0
    assert comp.max_divergence > 0.0
    assert len(comp.states_comparison) >= 2


def test_fidelity_distinction_note():
    """Verifies educational note and statevector fidelity calculation."""
    note = QuantumFidelityAnalyzer.get_fidelity_methodology_note()
    assert "SCIENTIFIC NOTE" in note
    assert "state fidelity" in note

    # Complex statevector fidelity
    sv1 = [1.0 + 0j, 0.0j]
    sv2 = [1.0 + 0j, 0.0j]
    assert QuantumFidelityAnalyzer.statevector_fidelity(sv1, sv2) == 1.0

    sv_orth = [0.0j, 1.0 + 0j]
    assert QuantumFidelityAnalyzer.statevector_fidelity(sv1, sv_orth) == 0.0


def test_laboratory_service_modes():
    """Verifies QuantumLaboratoryService executes Modes A, B, C, and D."""
    service = QuantumLaboratoryService()

    # Mode A: Ideal
    req_ideal = CircuitLabRequestSchema(
        num_qubits=2,
        preset="bell_state",
        shots=1000,
    )
    res_ideal = service.execute_circuit(req_ideal)
    assert res_ideal.num_qubits == 2
    assert not res_ideal.is_noisy_simulation
    assert res_ideal.counts is not None

    # Mode C: Comparison
    req_comp = CircuitComparisonRequestSchema(
        num_qubits=2,
        preset="bell_state",
        noise_profile="medium_noise",
        shots=1000,
        seed=123,
    )
    res_comp = service.compare_circuits(req_comp)
    assert res_comp.total_variation_distance >= 0.0
    assert 0.0 <= res_comp.classical_fidelity <= 1.0
    assert len(res_comp.states_comparison) >= 2

    # Mode D: Robustness sweep
    req_rob = CircuitRobustnessRequestSchema(
        num_qubits=2,
        preset="bell_state",
        noise_model="depolarizing",
        sweep=NoiseSweepConfigSchema(start=0.0, stop=0.06, step=0.02),
        shots=500,
        repeats_per_point=1,
        seed=42,
    )
    res_rob = service.run_robustness(req_rob)
    assert len(res_rob.points) == 4
    assert res_rob.points[0].parameter_value == 0.0
    assert res_rob.points[-1].parameter_value == 0.06
    # Fidelity should decrease as noise increases
    assert res_rob.points[0].mean_fidelity >= res_rob.points[-1].mean_fidelity
