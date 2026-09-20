"""
Bloop Circuit Robustness & Noise Sweep Analyzer
Conducts bounded, controlled noise sweeps across simulated quantum circuits to quantify
error susceptibility, fidelity decay, and target-state survival probabilities.
"""

import math
import statistics
import time
from typing import Callable, Dict, List, Optional
from qiskit import QuantumCircuit

from backend.app.quantum.config import quantum_config
from backend.app.quantum.laboratory.analysis.distributions import DistributionComparator
from backend.app.quantum.laboratory.analysis.measurements import MeasurementAnalyzer
from backend.app.quantum.laboratory.exceptions import (
    ExperimentTooLargeException,
    NoiseSweepTooLargeException,
)
from backend.app.quantum.laboratory.execution.executor import LaboratoryExecutor
from backend.app.quantum.laboratory.models import RobustnessPoint, RobustnessSweepResult
from backend.app.quantum.laboratory.noise.models import NoiseModelFactory
from backend.app.quantum.laboratory.schemas import NoiseModelConfigSchema, NoiseSweepConfigSchema


class RobustnessAnalyzer:
    """Executes noise parameter sweeps and calculates empirical robustness metrics."""

    def __init__(self, executor: Optional[LaboratoryExecutor] = None):
        self.executor = executor or LaboratoryExecutor()

    def run_sweep(
        self,
        circuit: QuantumCircuit,
        noise_model_type: str,
        sweep_config: NoiseSweepConfigSchema,
        shots: int = 1024,
        repeats_per_point: int = 1,
        target_state: Optional[str] = None,
        base_seed: Optional[int] = None,
    ) -> RobustnessSweepResult:
        """
        Executes a bounded noise parameter sweep.
        """
        max_steps = quantum_config.max_sweep_steps
        max_repeats = quantum_config.max_repeats

        repeats = min(max(repeats_per_point, 1), max_repeats)

        # Generate parameter grid
        param_values: List[float] = []
        curr = sweep_config.start
        step = sweep_config.step
        while curr <= sweep_config.stop + 1e-9:
            param_values.append(round(curr, 5))
            curr += step

        if len(param_values) > max_steps:
            raise NoiseSweepTooLargeException(
                f"Generated {len(param_values)} sweep steps, exceeding limit of {max_steps}.",
                details={"step_count": len(param_values), "max_steps": max_steps},
            )

        total_runs = len(param_values) * repeats
        if total_runs > 40:
            raise ExperimentTooLargeException(
                f"Total sweep runs ({total_runs}) exceeds safety limit of 40.",
                details={"total_runs": total_runs, "max_allowed": 40},
            )

        start_sweep_time = time.perf_counter()

        # Step 1: Run Ideal Baseline
        ideal_counts, _, _ = self.executor.execute_ideal(
            circuit=circuit,
            shots=shots,
            seed=base_seed,
            extract_statevector=False,
        )
        p_ideal = MeasurementAnalyzer.normalize_counts(ideal_counts, shots)
        dom_state, _ = MeasurementAnalyzer.get_dominant_state(p_ideal)
        tracked_target = target_state if target_state else dom_state

        points: List[RobustnessPoint] = []

        # Step 2: Iterate through sweep points
        for p_idx, p_val in enumerate(param_values):
            point_fidelities: List[float] = []
            point_tvds: List[float] = []
            point_target_probs: List[float] = []
            point_latencies: List[float] = []

            for r_idx in range(repeats):
                run_seed = (base_seed + p_idx * 10 + r_idx) if base_seed is not None else None

                # Construct noise model
                noise_cfg = NoiseModelConfigSchema(
                    model=noise_model_type,
                    probability=p_val,
                )
                noise_model = NoiseModelFactory.build_from_config(noise_cfg)

                if noise_model is None:
                    # Effectively zero noise
                    counts = ideal_counts
                    lat_ms = 1.0
                else:
                    counts, lat_ms = self.executor.execute_noisy(
                        circuit=circuit,
                        noise_model=noise_model,
                        shots=shots,
                        seed=run_seed,
                    )

                p_noisy = MeasurementAnalyzer.normalize_counts(counts, shots)
                fid = DistributionComparator.classical_fidelity(p_ideal, p_noisy)
                tvd = DistributionComparator.total_variation_distance(p_ideal, p_noisy)
                target_p = p_noisy.get(tracked_target, 0.0)

                point_fidelities.append(fid)
                point_tvds.append(tvd)
                point_target_probs.append(target_p)
                point_latencies.append(lat_ms)

            # Aggregate statistics
            mean_fid = round(statistics.mean(point_fidelities), 5)
            std_fid = round(statistics.stdev(point_fidelities), 5) if len(point_fidelities) > 1 else 0.0

            mean_tvd = round(statistics.mean(point_tvds), 5)
            std_tvd = round(statistics.stdev(point_tvds), 5) if len(point_tvds) > 1 else 0.0

            mean_target_p = round(statistics.mean(point_target_probs), 5)
            avg_lat = round(statistics.mean(point_latencies), 2)

            points.append(
                RobustnessPoint(
                    parameter_value=p_val,
                    mean_fidelity=mean_fid,
                    std_fidelity=std_fid,
                    mean_tvd=mean_tvd,
                    std_tvd=std_tvd,
                    success_probability=mean_target_p,
                    execution_time_ms=avg_lat,
                    repetition_count=repeats,
                )
            )

        total_sweep_time_ms = round((time.perf_counter() - start_sweep_time) * 1000.0, 2)

        # Formulate objective scientific summary
        first_pt = points[0]
        last_pt = points[-1]
        fid_drop = round(first_pt.mean_fidelity - last_pt.mean_fidelity, 4)

        summary_text = (
            f"Sweep across {len(points)} levels of {noise_model_type} noise "
            f"({sweep_config.start} to {sweep_config.stop}) resulted in fidelity change of "
            f"{first_pt.mean_fidelity:.4f} -> {last_pt.mean_fidelity:.4f} (Δ={fid_drop:+.4f}) "
            f"for target state |{tracked_target}⟩."
        )

        return RobustnessSweepResult(
            sweep_parameter=sweep_config.parameter,
            points=points,
            target_state=tracked_target,
            circuit_depth=circuit.depth(),
            total_gates=sum(circuit.count_ops().values()),
            total_runs=total_runs,
            total_execution_time_ms=total_sweep_time_ms,
            summary=summary_text,
        )
