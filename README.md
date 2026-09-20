# Bloop

> **Bloop** is a web-based AI Text-to-Speech application that converts user-provided text into natural speech through a secure Python FastAPI backend and ElevenLabs integration, while providing an isolated Quantum Intelligence environment for experimentation with quantum text encoding, affective emotion classification, semantic kernel similarity, circuit noise modeling, and empirical classical-vs-quantum benchmarking.

---

## Overview

Bloop bridges high-performance classical natural language processing, external voice synthesis providers, and quantum computational simulation into an intermediate-level, production-grade platform. 

The application provides:
1. **Core AI Text-to-Speech**: Reliable, authenticated speech synthesis with dynamic voice discovery, capability-based validation, streaming audio playback, and personalized history and favorites curation.
2. **Quantum Intelligence (Optional Side-Car)**: Educational and research-oriented quantum simulation modules utilizing Qiskit and PennyLane for feature encoding, hybrid QNN affective classification, quantum kernel state fidelity, circuit noise simulation, and multi-category benchmarking.
3. **Hybrid Speech Intelligence**: Mathematical score, feature, and decision fusion that produces decoupled acoustic recommendations (`speed`, `pitch`, `stability`, `similarity_boost`, `pacing`) with dynamic voice capability verification.
4. **Authoritative Decoupled Architecture**: The core Text-to-Speech engine operates completely independently of quantum computing components. Any quantum timeout, simulator error, or subsystem deactivation never degrades or interrupts speech synthesis.

---

## Features

- **Text Workspace**: Character and word counting, whitespace normalization, multi-language selection, dynamic voice capability filtering, and empty text rejection.
- **Dynamic Voice Discovery**: Provider-independent voice management dynamically validated against language capabilities without hardcoded or fabricated voice catalogues.
- **Robust Audio Delivery**: HTML5 audio player with waveform visualizer, playback rate controls, seeking, volume adjustment, and authorized download.
- **User Curation**: Personal speech history, audio playback persistence, favoriting, metadata inspection, and search filtering.
- **Quantum Text Intelligence**: Hilbert space angle encoding, TruncatedSVD feature reduction, and Variational Quantum Classification (VQC) compared against classical TF-IDF Logistic Regression.
- **Quantum Emotion Intelligence**: PennyLane hybrid Quantum Neural Network (QNN) measuring Pauli-Z expectation values and von Neumann entanglement entropy.
- **Quantum Semantic Intelligence**: Quantum state fidelity transition kernels evaluating semantic pair similarity and matrix comparisons.
- **Quantum Circuit & Noise Laboratory**: Bounded circuit builder with approved gate whitelisting, depolarizing/thermal noise injection, and robustness parameter sweeps.
- **Empirical Multi-Category Benchmarking**: Reproducible, zero-data-leakage benchmarks across 5 categories (Text, Emotion, Semantic, Circuit, Pipeline) with honest classical CPU speedup reporting.
- **Security Hardening**: Argon2id/Bcrypt password hashing, PyJWT bearer sessions, defensive security headers (HSTS, nosniff, DENY framing), CORS environment protection, and payload size limits.

---

## Architecture

Bloop follows an authoritative decoupled monorepo topology:

```text
                    ┌─────────────────────┐
                    │       GitHub        │
                    │ Source + Workflow   │
                    └──────────┬──────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
        ┌─────────────────┐         ┌─────────────────┐
        │     Vercel      │         │     Render      │
        │ React + Vite    │ HTTPS   │    FastAPI      │
        │ TypeScript      │◄───────►│    Backend      │
        └─────────────────┘         └────────┬────────┘
                                             │
                           ┌─────────────────┼──────────────────┐
                           │                 │                  │
                           ▼                 ▼                  ▼
                    ┌────────────┐   ┌──────────────┐   ┌──────────────┐
                    │ PostgreSQL │   │  ElevenLabs  │   │   Quantum    │
                    │   Render   │   │     TTS      │   │ Intelligence │
                    └────────────┘   └──────────────┘   └──────────────┘
```

### Production Dependency Chains

1. **Core Speech Synthesis Pipeline**:
   ```text
   React (Vercel) ──► FastAPI (Render) ──► SpeechService ──► ElevenLabsProvider ──► Audio Stream
   ```
2. **Quantum Intelligence Side-Car (Optional)**:
   ```text
   React (Vercel) ──► FastAPI (Render) ──► QuantumService ──► Qiskit Aer / PennyLane
   ```
3. **Hybrid Recommendation Pipeline (Upstream & Optional)**:
   ```text
   Text Input ──► Classical Baseline + Quantum State ──► Mathematical Fusion ──► Acoustic Recommendation ──► User Apply / Ignore ──► SpeechService
   ```

---

## Technology Stack

### Frontend Client
- **Framework**: React 19 + TypeScript + Vite
- **Styling**: Tailwind CSS + Glassmorphism aesthetic tokens
- **Routing**: React Router 7 SPA with Vercel edge rewrite configuration
- **Server Cache & State**: TanStack Query v5 + Zustand
- **Testing**: Vitest + React Testing Library

### Backend API
- **Framework**: Python 3.11+ / 3.12 FastAPI
- **ORM & Migrations**: SQLAlchemy 2.0 + Alembic (PostgreSQL in production / SQLite local fallback)
- **Validation**: Pydantic v2 + Pydantic-Settings
- **Security**: Argon2id / Passlib + PyJWT
- **Testing**: Pytest + FastAPI TestClient + HTTPX

### Quantum & Machine Learning Subsystems
- **Qiskit 2.x & Qiskit Aer**: State preparation, angle encoding, Variational Quantum Classifiers (VQC), and Kraus decoherence noise channels
- **PennyLane**: Differentiable quantum neural networks with `default.qubit` and `qiskit.aer` devices
- **Scikit-Learn & NumPy**: Sublinear TF-IDF vectorization, TruncatedSVD dimensionality reduction, Logistic Regression baselines

---

## Quantum Intelligence

The Quantum Intelligence Subsystem is simulation-first and runs on classical CPU simulators without requiring cloud quantum hardware accounts:

1. **Text Style Classification**: Maps text into $N \le 8$ qubit angles $\theta_i \in [0, \pi]$ using single-qubit $R_y(\theta_i)$ rotations and alternating CNOT entanglers.
2. **Emotion Intelligence (QNN)**: Parameterized variational circuit evaluating Pauli-Z expectation values across 4 affective classes (joy, sadness, anger, neutral).
3. **Semantic Similarity Kernel**: Evaluates state transition fidelity $K(A, B) = |\langle 0\dots 0 | U^\dagger(x_B) U(x_A) | 0\dots 0 \rangle|^2$ for pairwise similarity estimation.
4. **Circuit & Noise Laboratory**: Simulates physical decoherence (depolarization, bit-flip, phase-flip, bit-phase-flip, thermal relaxation with $T_2 \le 2T_1$, and readout error) measuring Total Variation Distance (TVD) and Bhattacharyya Classical Fidelity.
5. **Multi-Category Benchmarking**: Standardized, reproducible train/test splits with seed tracking, comparing classical CPU execution speedups against quantum simulation overhead.

> [!NOTE]
> **Scientific Integrity**: Bloop reports purely empirical metrics and explicitly acknowledges that classical heuristic models run faster on classical CPUs than simulated quantum statevectors. No false claims of "quantum supremacy" or "quantum advantage" are made.

---

## Project Structure

```text
bloop/
├── .github/
│   └── workflows/
│       ├── ci.yml                    # Automated CI test and build workflow
│       └── audit.yml                 # Security vulnerability audit workflow
│
├── backend/
│   ├── alembic/                      # Database migrations
│   ├── app/
│   │   ├── api/                      # Versioned FastAPI endpoints (/api/v1/*)
│   │   ├── core/                     # Settings, security headers, middleware, logging
│   │   ├── db/                       # SQLAlchemy engine, session, and initialization
│   │   ├── models/                   # ORM domain models (User, Preference, Voice, etc.)
│   │   ├── schemas/                  # Pydantic request/response schemas
│   │   ├── services/                 # Business logic services (Auth, Speech, Voice, etc.)
│   │   └── quantum/                  # Isolated Quantum Intelligence Subsystem
│   │       ├── text/                 # Quantum text encoding & classification
│   │       ├── emotion/              # Quantum emotion intelligence & QNN
│   │       ├── semantic/             # Quantum semantic similarity & kernel
│   │       ├── laboratory/           # Circuit builder, noise models & sweeps
│   │       └── hybrid/               # Multi-category benchmarks & speech bridge
│   ├── tests/                        # Backend test suites (unit, api, security, quantum)
│   ├── requirements.txt              # Production Python dependencies
│   └── requirements-dev.txt          # Development & testing dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/               # UI components (AudioPlayer, Modal, Button, etc.)
│   │   ├── features/                 # Domain features (tts, history, favorites, quantum)
│   │   ├── pages/                    # Workspace, Dashboard, History, Quantum views
│   │   ├── services/                 # Centralized HTTP API client
│   │   └── stores/                   # Zustand state stores
│   ├── tests/                        # Vitest unit and integration tests
│   ├── package.json                  # Frontend dependencies and scripts
│   ├── tsconfig.json                 # TypeScript compiler configuration
│   ├── vercel.json                   # Vercel deployment rewrites & security headers
│   └── vite.config.ts                # Vite build pipeline
│
├── docs/                             # Architecture specs, ADRs, user journeys, requirements
├── tests/smoke/                      # End-to-end release and system smoke tests
├── render.yaml                       # Render Web Service & PostgreSQL blueprint
└── .gitignore                        # Strict secret & artifact exclusion rules
```

---

## Local Development

### Prerequisites
- Python 3.11 or 3.12
- Node.js 20 LTS and npm
- PostgreSQL (optional locally; SQLite is used as local development fallback)

### Backend Setup
```bash
# 1. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate    # Linux/macOS
# .venv\Scripts\activate     # Windows

# 2. Install dependencies
pip install -r backend/requirements.txt
pip install -r backend/requirements-dev.txt

# 3. Configure environment
cp .env.example backend/.env

# 4. Run database migrations
alembic upgrade head

# 5. Start FastAPI development server
uvicorn backend.app.main:app --reload --port 8000
```

### Frontend Setup
```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm ci

# 3. Configure environment
cp .env.example .env

# 4. Start Vite development server
npm run dev
```

The frontend will be available at `http://localhost:5173` and the backend API at `http://localhost:8000`.

---

## Environment Variables

| Variable | Description | Development Default | Production Required |
| :--- | :--- | :--- | :--- |
| `APP_ENV` | Runtime environment name | `development` | `production` |
| `APP_DEBUG` | Enable debug mode & docs | `true` | `false` |
| `DATABASE_URL` | PostgreSQL connection string | `sqlite:///./bloop.db` | Render PostgreSQL URL |
| `JWT_SECRET_KEY` | Cryptographic signing secret | Dev placeholder | High-entropy secret ($\ge 32$ chars) |
| `ELEVENLABS_API_KEY`| ElevenLabs provider API key | `""` (Simulation mode) | Real ElevenLabs API Key |
| `CORS_ORIGINS` | Permitted frontend origins | `http://localhost:5173,http://localhost:3000` | `https://bloop.vercel.app` |
| `QUANTUM_ENABLED` | Toggle quantum subsystem | `true` | `true` |
| `RATE_LIMIT_ENABLED`| API abuse rate limiting | `true` | `true` |
| `VITE_API_BASE_URL` | Public frontend API base URL | `http://localhost:8000` | Render Backend URL |

---

## API

All API endpoints reside under `/api/v1/*` and return standard JSON response envelopes:

```json
// Success Response
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully."
}

// Error Response
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Sanitized human-readable error description."
  }
}
```

### Key API Domains:
- **System**: `GET /api/v1/health`, `GET /api/v1/health/live`, `GET /api/v1/health/ready`
- **Authentication**: `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `POST /api/v1/auth/logout`
- **Speech**: `GET /api/v1/languages`, `GET /api/v1/voices`, `POST /api/v1/tts`
- **Curation**: `GET /api/v1/history`, `GET /api/v1/favorites`, `POST /api/v1/favorites`
- **Quantum**:
  - `POST /api/v1/quantum/text`: Angle encoding and VQC style classification
  - `POST /api/v1/quantum/emotion`: Affective PennyLane QNN classification
  - `POST /api/v1/quantum/semantic`: Quantum state transition kernel similarity
  - `POST /api/v1/quantum/circuit`: Interactive simulation (ideal and noisy)
  - `POST /api/v1/quantum/benchmark`: Multi-category empirical benchmarking (Types A–E)
  - `POST /api/v1/quantum/hybrid/recommend`: Decoupled acoustic speech parameter recommendation

---

## Testing

The project implements a complete testing pyramid across backend and frontend:

### Backend Test Suite (Pytest)
```bash
# Run all unit, security, and quantum tests
pytest backend/tests -v

# Run system smoke tests
pytest tests/smoke -v
```
*Current test metrics: **151/151** full quantum tests passing, **12/12** core TTS/Auth regression tests passing, **6/6** security hardening tests passing, **2/2** smoke test suites passing.*

### Frontend Test Suite (Vitest)
```bash
cd frontend
npm test
```
*Current test metrics: **148/148** frontend unit and integration tests passing across 16 test files (100% pass rate).*

---

## GitHub Workflow

The repository uses GitHub as the authoritative source of truth:
- **Branching Model**: Simple `main` branch deployment flow. Feature branches (`feature/*`, `fix/*`) merge into `main` via pull requests.
- **CI Pipeline (`.github/workflows/ci.yml`)**:
  1. Sets up Python 3.11 and Node.js 20 LTS environments.
  2. Runs database migrations (`alembic upgrade head`).
  3. Executes backend test suites (`pytest backend/tests tests -v`).
  4. Runs frontend test suites (`npm test`).
  5. Validates TypeScript types and production build (`npm run build`).
- **Security Audit Pipeline (`.github/workflows/audit.yml`)**:
  - Runs automated vulnerability scanning across Python packages (`pip-audit`) and npm packages (`npm audit`).

---

## Render Deployment

The backend is configured for deployment as a Render Web Service with managed Render PostgreSQL via [`render.yaml`](render.yaml):

1. Connect the GitHub repository in the Render Dashboard.
2. Select Blueprint deployment using `render.yaml`.
3. Configure environment secrets in the Render dashboard:
   - `ELEVENLABS_API_KEY`: Real API key from ElevenLabs.
   - `JWT_SECRET_KEY`: High-entropy production cryptographic key.
   - `CORS_ORIGINS`: `https://your-app.vercel.app`.
4. Build command automatically applies database migrations:
   ```bash
   pip install -r backend/requirements.txt && alembic upgrade head
   ```
5. Start command launches Uvicorn:
   ```bash
   uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
   ```
6. Health probe endpoint: `/api/v1/health`.

---

## Vercel Deployment

The frontend SPA is configured for zero-configuration deployment to Vercel via [`frontend/vercel.json`](frontend/vercel.json):

1. Connect the GitHub repository in the Vercel Dashboard.
2. Set Root Directory to `frontend`.
3. Build Settings:
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Environment Variables:
   - `VITE_API_BASE_URL`: `https://your-bloop-backend.onrender.com`
5. [`vercel.json`](frontend/vercel.json) enforces SPA URL rewrites to `/index.html` and attaches defensive HTTP security headers.

---

## Production Configuration

| Environment Property | Production Enforcement |
| :--- | :--- |
| `APP_DEBUG` | Strictly `false` (Disables `/docs` and raw stack traces) |
| `DATABASE_URL` | Persistent Render PostgreSQL URL (SQLite strictly prohibited in production) |
| `CORS_ORIGINS` | Explicit Vercel domain only (Wildcard `*` strictly rejected at startup) |
| `JWT_SECRET_KEY` | Must be $\ge 32$ characters from environment; defaults prohibited |
| `ELEVENLABS_API_KEY` | Server-side only; never exposed to frontend client or build bundles |
| `Strict-Transport-Security` | Enabled with `max-age=31536000; includeSubDomains` |

---

## Security

Bloop adheres to strict defensive security practices:
- **Authentication**: Salted password hashing with Argon2id; stateless JWT bearer tokens with configurable expiration; opaque login error messages preventing user enumeration.
- **Authorization**: Strict database-level tenant isolation; user-owned resources (generations, history, favorites, quantum experiments) enforce `user_id` ownership checks on every read and write.
- **HTTP Security Headers**: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block`, `Referrer-Policy: strict-origin-when-cross-origin`, and production HSTS.
- **Input Validation**: Pydantic v2 schemas reject malformed payloads, non-finite float angles, unapproved quantum gates, and oversized text bodies before executing business logic.
- **Quantum Guardrails**: Zero `eval()`, `exec()`, or dynamic code imports; strict resource bounds ($N \le 8$ qubits, shots $\le 8192$, circuit depth $\le 30$, execution timeout 30s).
- **Error Sanitization**: Production exceptions return clean, standardized error envelopes without stack traces, database internals, or provider secrets.

---

## Copyright

Copyright © 2026 Bloop. All rights reserved.
