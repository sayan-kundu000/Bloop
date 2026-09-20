import time
import math
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

from backend.app.core.logging import logger
from backend.app.quantum.features import TextFeatureExtractor
from backend.app.quantum.semantic_kernel import QuantumSemanticEstimator
from backend.app.quantum.emotion_qnn import QuantumEmotionAnalyzer
from backend.app.quantum.voice_rag import VoiceRAGService


@dataclass
class QuantumVoiceModulationResult:
    voice_id: str
    character_name: str
    canonical_source: str
    prompt_text: str
    quantum_fidelity: float
    quantum_emotion: str
    entanglement_entropy: float
    resonance_verdict: str
    effective_pitch_str: str
    effective_rate_str: str
    dsp_profile: Dict[str, Any]
    audio_video_reference: Dict[str, Any]
    quantum_decision: Dict[str, Any]
    execution_time_ms: float


class ParameterizedQuantumDecisionCircuit:
    """
    4-Qubit Variational Quantum Decision Circuit.
    Entangles text prompt features with character audio/video acoustic benchmarks.
    Measures Pauli-Z expectation values <Z_0>, <Z_1>, <Z_2>, <Z_3> to autonomously
    decide dynamic pitch offset, speech rate, delivery mode, and DSP filter parameters.
    """

    def __init__(self, num_qubits: int = 4):
        self.num_qubits = 4
        self.simulator = AerSimulator()

    def evaluate_decision(
        self,
        phi_prompt: np.ndarray,
        theta_ref: np.ndarray,
        shots: int = 1024,
    ) -> tuple[List[float], Dict[str, int], float]:
        """
        Executes the parameterized decision circuit.
        Returns:
            pauli_z_expectations: [<Z0>, <Z1>, <Z2>, <Z3>]
            counts: bitstring measurement counts
            circuit_fidelity: quantum state overlap estimate
        """
        qc = QuantumCircuit(4, 4)

        # 1. Initialize Superposition
        for i in range(4):
            qc.h(i)

        # 2. Angle Encoding of Text Prompt Features
        for i in range(4):
            qc.ry(float(phi_prompt[i]), i)

        # 3. Parameterized Entangling Layer (Couples semantic intent to acoustic traits)
        qc.cx(0, 1)
        qc.cx(1, 2)
        qc.cx(2, 3)
        qc.cx(3, 0)

        # 4. Phase Rotation of Character Audio/Video Reference Benchmark
        for i in range(4):
            qc.rz(float(theta_ref[i]), i)

        # 5. Variational Mixing Layer
        for i in range(4):
            qc.ry(float((phi_prompt[i] + theta_ref[i]) / 2.0), i)

        # 6. Measure all qubits
        qc.measure(range(4), range(4))

        compiled = transpile(qc, self.simulator)
        job = self.simulator.run(compiled, shots=shots)
        result = job.result()
        counts = result.get_counts()

        # Calculate Pauli-Z expectation values: <Z_i> in [-1.0, 1.0]
        # In Qiskit, bitstring[3 - i] corresponds to qubit i
        z_exp = [0.0] * 4
        total_shots = sum(counts.values())

        for bitstring, count in counts.items():
            for i in range(4):
                bit = bitstring[3 - i]
                val = 1.0 if bit == '0' else -1.0
                z_exp[i] += val * count

        z_exp = [round(z / total_shots, 4) for z in z_exp]

        # Calculate quantum fidelity from the probability of observing ground state |0000>
        p_ground = counts.get('0000', 0) / total_shots
        # Normalized fidelity metric
        circuit_fidelity = round(min(max(p_ground * 4.0, 0.15), 1.0), 4)

        return z_exp, counts, circuit_fidelity


class QuantumVoiceModulator:
    """
    Quantum-RAG Character Voice Modulator & Decision Engine.
    Grounded in concrete Audio/Video reference scenes and acoustic benchmarks.
    Uses Qiskit Aer Parameterized Quantum Decision Circuits (PQDC) and PennyLane
    to calculate dynamic voice acoustic parameters, delivery mode, and DSP modulation.
    """

    def __init__(self):
        self.rag = VoiceRAGService()
        self.feature_extractor = TextFeatureExtractor(num_qubits=4)
        self.semantic_estimator = QuantumSemanticEstimator(num_qubits=4)
        self.emotion_analyzer = QuantumEmotionAnalyzer(shots=512)
        self.decision_circuit = ParameterizedQuantumDecisionCircuit(num_qubits=4)

    def modulate_voice(
        self,
        voice_id: str,
        prompt_text: str,
        user_speed: float = 1.0,
        user_pitch: float = 1.0,
        emotion: Optional[str] = "Neutral",
    ) -> QuantumVoiceModulationResult:
        start_time = time.perf_counter()
        clean_emotion = (emotion or "Neutral").strip().title()

        # 1. RAG Context Retrieval (Lore + Concrete Audio/Video Reference)
        rag_context = self.rag.retrieve_augmented_context(voice_id, prompt_text)
        lore_text = rag_context["lore_text"]
        vocal_sig = rag_context["vocal_signature"]
        base_dsp = dict(rag_context["acoustic_dsp"])
        media_ref = rag_context.get("audio_video_reference", {})
        benchmark = media_ref.get("acoustic_benchmark", {})

        # 2. Extract Acoustic Benchmark Parameters from Audio/Video Reference
        ref_f0 = float(benchmark.get("f0_median_hz", 130.0))
        ref_wpm = float(benchmark.get("tempo_wpm", 125.0))
        ref_grit = float(benchmark.get("vocal_grit", 0.3))
        ref_f1 = float(benchmark.get("formant_f1_hz", 500.0))
        ref_f2 = float(benchmark.get("formant_f2_hz", 1400.0))
        formant_ratio = ref_f2 / max(ref_f1, 100.0)

        # Map reference benchmark into phase angles theta_ref in [-pi, pi]
        theta_ref = np.array([
            math.pi * ((ref_f0 - 130.0) / 100.0),
            math.pi * ((ref_wpm - 125.0) / 80.0),
            math.pi * ((ref_grit - 0.5) * 2.0),
            math.pi * ((formant_ratio - 2.8) / 2.0),
        ])

        # 3. Extract Prompt Text Feature Vector phi_prompt in [-pi, pi]
        raw_prompt_vec = self.feature_extractor.extract_features(prompt_text)
        phi_prompt = np.array([float(x) for x in raw_prompt_vec[:4]])

        # 4. PennyLane Quantum Emotion Analysis
        try:
            emotion_res = self.emotion_analyzer.analyze(prompt_text)
            detected_emotion = emotion_res.detected_emotion
            entropy = emotion_res.entanglement_entropy
        except Exception as e_err:
            logger.warning(f"Quantum emotion analysis fallback ({e_err})")
            detected_emotion = "neutral"
            entropy = 1.38

        # 5. Parameterized Quantum Decision Circuit Execution (Decides Everything!)
        try:
            z_exp, counts, circuit_fidelity = self.decision_circuit.evaluate_decision(
                phi_prompt=phi_prompt,
                theta_ref=theta_ref,
                shots=1024,
            )
        except Exception as q_err:
            logger.warning(f"PQDC execution fallback ({q_err})")
            z_exp = [0.0, 0.0, 0.0, 0.0]
            counts = {'0000': 1024}
            circuit_fidelity = 0.55

        # 6. Quantum Kernel Semantic State Overlap
        try:
            semantic_res = self.semantic_estimator.compare(prompt_text, lore_text)
            quantum_fidelity = semantic_res.quantum_kernel_similarity
            resonance_verdict = semantic_res.similarity_verdict
        except Exception:
            quantum_fidelity = circuit_fidelity
            resonance_verdict = "Quantum Reference Aligned"

        # Keyword boost from RAG
        kw_boost = rag_context.get("keyword_resonance_score", 0.0)
        composite_fidelity = round(min(quantum_fidelity * 0.65 + kw_boost * 0.35, 1.0), 4)

        # Emotion Acoustic Offsets
        EMOTION_OFFSETS = {
            "Happy": (18, 10, "Rapid-Fire Staccato Rhythm & Articulation"),
            "Joyful": (22, 12, "Rapid-Fire Staccato Rhythm & Articulation"),
            "Excited": (28, 18, "Fierce Explosive Overdrive & Battle Cry"),
            "Enthusiastic": (24, 15, "Rapid-Fire Staccato Rhythm & Articulation"),
            "Ecstatic": (35, 24, "Fierce Explosive Overdrive & Battle Cry"),
            "Eager": (20, 14, "Rapid-Fire Staccato Rhythm & Articulation"),
            "Cheerful": (16, 10, "Rapid-Fire Staccato Rhythm & Articulation"),
            "Playful": (16, 10, "Rapid-Fire Staccato Rhythm & Articulation"),
            "Angry": (25, 16, "Fierce Explosive Overdrive & Battle Cry"),
            "Furious": (35, 24, "Fierce Explosive Overdrive & Battle Cry"),
            "Intense": (18, 12, "Fierce Explosive Overdrive & Battle Cry"),
            "Urgent": (24, 20, "Fierce Explosive Overdrive & Battle Cry"),
            "Annoyed": (14, 10, "Fierce Explosive Overdrive & Battle Cry"),
            "Frustrated": (16, 10, "Fierce Explosive Overdrive & Battle Cry"),
            "Sad": (-22, -16, "Intimate Hypnotic Cadence & Monologue"),
            "Heartbroken": (-26, -20, "Intimate Hypnotic Cadence & Monologue"),
            "Melancholic": (-20, -16, "Intimate Hypnotic Cadence & Monologue"),
            "Lonely": (-18, -14, "Intimate Hypnotic Cadence & Monologue"),
            "Disappointed": (-16, -12, "Intimate Hypnotic Cadence & Monologue"),
            "Whispering": (-22, -20, "Intimate Hypnotic Cadence & Monologue"),
            "Mysterious": (-18, -14, "Intimate Hypnotic Cadence & Monologue"),
            "Romantic": (-12, -14, "Intimate Hypnotic Cadence & Monologue"),
            "Seductive": (-14, -16, "Intimate Hypnotic Cadence & Monologue"),
            "Terrified": (32, 24, "Rapid-Fire Staccato Rhythm & Articulation"),
            "Fearful": (24, 16, "Rapid-Fire Staccato Rhythm & Articulation"),
            "Anxious": (20, 14, "Rapid-Fire Staccato Rhythm & Articulation"),
            "Nervous": (18, 12, "Rapid-Fire Staccato Rhythm & Articulation"),
            "Calm": (-8, -10, "Balanced Canonical Narrative"),
            "Peaceful": (-10, -12, "Balanced Canonical Narrative"),
            "Relaxed": (-8, -10, "Balanced Canonical Narrative"),
            "Sleepy": (-18, -24, "Intimate Hypnotic Cadence & Monologue"),
            "Authoritative": (-16, -4, "Authoritative Gravitas & Regal Presence"),
            "Serious": (-14, -6, "Authoritative Gravitas & Regal Presence"),
            "Determined": (-10, 6, "Authoritative Gravitas & Regal Presence"),
            "Triumphant": (26, 16, "Authoritative Gravitas & Regal Presence"),
        }
        emo_data = EMOTION_OFFSETS.get(clean_emotion, (0, 0, None))
        emo_pitch_shift, emo_rate_shift, emo_mode = emo_data

        # Qubit 0 Expectation <Z0> -> Decides Continuous Pitch Shift
        base_pitch = vocal_sig.get("base_pitch_hz", 0)
        quantum_pitch_shift = int(round(z_exp[0] * 12.0 + (ref_f0 - 130.0) * 0.22))
        user_pitch_delta = int(round((user_pitch - 1.0) * 40))
        total_pitch = base_pitch + quantum_pitch_shift + user_pitch_delta + emo_pitch_shift
        total_pitch = max(min(total_pitch, 90), -60)

        # Qubit 1 Expectation <Z1> -> Decides Speech Rate & Cadence
        base_rate = vocal_sig.get("base_rate_pct", 0)
        quantum_rate_shift = int(round(z_exp[1] * 15.0 + (ref_wpm - 125.0) * 0.20))
        user_rate_delta = int(round((user_speed - 1.0) * 100))
        total_rate = base_rate + quantum_rate_shift + user_rate_delta + emo_rate_shift
        total_rate = max(min(total_rate, 80), -40)

        # Qubit 2 Expectation <Z2> -> Decides DSP Saturation & Drive
        dsp_drive_scaling = max(0.6, min(1.0 + (z_exp[2] * 0.45), 1.7))
        if "drive" in base_dsp:
            base_dsp["drive"] = round(float(base_dsp["drive"]) * dsp_drive_scaling, 2)
        if "wet_mix" in base_dsp:
            base_dsp["wet_mix"] = round(min(float(base_dsp["wet_mix"]) * (0.85 + z_exp[2] * 0.3), 0.85), 2)

        # Qubit 3 Expectation <Z3> -> Decides Formant / Bass Boost Intensity
        if "bass_boost_db" in base_dsp:
            base_dsp["bass_boost_db"] = round(max(float(base_dsp["bass_boost_db"]) + z_exp[3] * 2.0, 1.0), 1)

        # Determine Vocal Delivery Mode from Projective Measurement Probability
        top_bitstrings = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        dominant_mode_bits = top_bitstrings[0][0][:2] if top_bitstrings else "00"
        delivery_mode_map = {
            "00": "Authoritative Gravitas & Regal Presence",
            "01": "Fierce Explosive Overdrive & Battle Cry",
            "10": "Intimate Hypnotic Cadence & Monologue",
            "11": "Rapid-Fire Staccato Rhythm & Articulation",
        }
        decided_mode = emo_mode if (emo_mode and clean_emotion != "Neutral") else delivery_mode_map.get(dominant_mode_bits, "Balanced Canonical Narrative")

        effective_pitch_str = f"{total_pitch:+d}Hz"
        effective_rate_str = f"{total_rate:+d}%"

        decision_rationale = (
            f"Quantum observable <Z0>={z_exp[0]:+.3f} (emotion '{clean_emotion}') resolved continuous pitch to {effective_pitch_str} "
            f"(anchored to reference F0={ref_f0:.1f}Hz). "
            f"<Z1>={z_exp[1]:+.3f} resolved speech tempo to {effective_rate_str} "
            f"(anchored to reference tempo={ref_wpm:.0f} WPM). "
            f"<Z2>={z_exp[2]:+.3f} tuned acoustic DSP drive & wet mix. "
            f"Measurement projection resolved delivery mode: '{decided_mode}'."
        )

        quantum_decision_details = {
            "pauli_z_expectations": z_exp,
            "decided_pitch_hz": total_pitch,
            "decided_rate_pct": total_rate,
            "decided_dsp_filter": base_dsp.get("filter_type", "natural_warmth"),
            "decided_delivery_mode": decided_mode,
            "decision_rationale": decision_rationale,
        }

        execution_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return QuantumVoiceModulationResult(
            voice_id=voice_id,
            character_name=rag_context["character_name"],
            canonical_source=rag_context["canonical_source"],
            prompt_text=prompt_text,
            quantum_fidelity=composite_fidelity,
            quantum_emotion=detected_emotion,
            entanglement_entropy=round(entropy, 4),
            resonance_verdict=resonance_verdict,
            effective_pitch_str=effective_pitch_str,
            effective_rate_str=effective_rate_str,
            dsp_profile=base_dsp,
            audio_video_reference=media_ref,
            quantum_decision=quantum_decision_details,
            execution_time_ms=execution_time_ms,
        )
