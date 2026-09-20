"""
Backend Test Fixtures & Sample Inputs
"""

SAMPLE_TTS_PAYLOAD = {
    "text": "Hello world, welcome to Bloop speech synthesis.",
    "voice_id": "test-voice-id",
    "language": "en-US",
    "speed": 1.0,
    "pitch": 1.0,
}

SAMPLE_QUANTUM_CIRCUIT = {
    "num_qubits": 2,
    "shots": 512,
    "gates": [
        {"gate": "h", "target": 0},
        {"gate": "cx", "control": 0, "target": 1},
    ],
}
