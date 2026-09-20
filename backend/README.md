# Bloop — Backend Application Architecture

The Bloop backend is an asynchronous, high-throughput REST API engine developed with **Python 3.11+**, **FastAPI**, **Pydantic v2**, **SQLAlchemy 2.0**, and **Alembic**.

```
backend/
├── alembic/            # Versioned database migration revisions
├── app/
│   ├── api/            # API endpoints & dependencies (/api/v1/*)
│   ├── core/           # Configuration, security (JWT/bcrypt), logging
│   ├── db/             # SQLAlchemy session factory & base model
│   ├── models/         # Declarative ORM entities (User, SpeechGeneration, Voice)
│   ├── schemas/        # Pydantic v2 request/response schemas
│   ├── repositories/   # Encapsulated database access objects
│   ├── services/       # Domain business logic orchestrators
│   ├── providers/      # BaseTTSProvider, ElevenLabsProvider, SimulationTTSProvider
│   ├── quantum/        # 5 Isolated Quantum Intelligence Engines
│   ├── storage/        # Audio disk storage & HTTP 206 byte-range streamer
│   └── main.py         # FastAPI application entrypoint
├── tests/              # Unit, API, Provider, and Quantum test suites
├── requirements.txt    # Production Python dependencies
├── requirements-dev.txt# Dev & testing tools
├── pytest.ini          # Pytest runner configuration
└── voices_config.json  # File-based dynamic voice ingestion registry
```

## Running Locally

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Or .\.venv\Scripts\Activate.ps1 on Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8000
```

## Quantum Computing Foundation

The backend includes an isolated, simulation-first **Quantum Computing Foundation Layer**:
- **Qiskit & Qiskit Aer**: Gate-level circuit sandbox, custom circuits, OpenQASM export, and depolarizing noise simulation.
- **PennyLane & PennyLane-Qiskit**: Parameterized circuits, variational layers, and Qiskit Aer device interoperability.
- **Qiskit Machine Learning**: Quantum kernel statevector methods (`FidelityStatevectorKernel`).
- **Hybrid Quantum-Classical ML**: Safe angle feature normalization, empirical train/test benchmarks against classical baselines (Logistic Regression).
- **Decoupled Architecture**: Quantum simulation failures never affect the core Text-to-Speech synthesis pipeline.

## Running Tests

```bash
pytest tests/ -v
```

