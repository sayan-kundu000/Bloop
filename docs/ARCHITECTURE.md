# Bloop — Full-Stack System Architecture & Technical Design

**Document Identifier:** BLOOP-ARCH-V1  
**Project:** Bloop — AI Text-to-Speech & Quantum Intelligence Platform  
**Target Milestone:** Intermediate-Level Full-Stack Architecture  
**Status:** Approved Architectural Baseline  
**Authority:** Bloop Master Prompt & Prompt 02

---

## Architecture Document Suite Index

This master document summarizes the system design. For in-depth domain specifications, consult the dedicated architecture suite:

- 🏛️ **[System Architecture](architecture/system-architecture.md)** — Master topology, boundaries, and traceability
- 🛠️ **[Technology Stack & Decision Matrix](architecture/technology-stack.md)** — Definitive full-stack technology blueprint and trade-off analysis
- 📦 **[Dependency Strategy & Package Policy](architecture/dependency-strategy.md)** — Python & Node dependency boundaries, state contracts, and minimalism
- 🔄 **[Runtime Compatibility Matrix](architecture/runtime-compatibility.md)** — Cross-stack verification across Python, Node, Vite, Qiskit, PennyLane, and PaaS
- 🔐 **[Environment & Secret Management](architecture/environment-strategy.md)** — Twelve-Factor environment configuration and secret isolation
- 💻 **[Frontend Architecture](architecture/frontend-architecture.md)** — React 19, Vite, TanStack Query, Zustand, and audio player
- ⚙️ **[Backend Architecture](architecture/backend-architecture.md)** — FastAPI, services, repositories, providers, and security
- 🗄️ **[Database Architecture](architecture/database-architecture.md)** — PostgreSQL 16 schema, ERD, indexes, and Alembic migrations
- 🌐 **[REST API Architecture](architecture/api-architecture.md)** — OpenAPI specification, JSON envelopes, and endpoint catalog
- 🎙️ **[TTS Data Flow](architecture/tts-data-flow.md)** — 21-step canonical speech pipeline, audio streaming, and fallback
- ⚛️ **[Quantum Architecture](architecture/quantum-architecture.md)** — Qiskit Aer VQC, PennyLane QNN, circuit lab, and benchmarks
- 🚀 **[Deployment Architecture](architecture/deployment-architecture.md)** — Render, Vercel, CI/CD, and environment configuration

### Development & Deployment Runbooks
- 💻 **[Local Development Setup Guide](development/local-setup.md)** — Onboarding, virtual environment, migrations, and local dev server
- 🛡️ **[Dependency Management Policy](development/dependency-management.md)** — Package governance, vulnerability scanning, and audit rules
- ☁️ **[Render Deployment Runbook](deployment/render.md)** — FastAPI web service and managed PostgreSQL deployment
- ⚡ **[Vercel Deployment Runbook](deployment/vercel.md)** — React 19 SPA Edge distribution and client routing rewrites

### Architecture Decision Records (ADRs)
- [ADR-001: React 19 + TypeScript](architecture/adr/ADR-001-react-typescript.md)
- [ADR-002: FastAPI Async REST API](architecture/adr/ADR-002-fastapi.md)
- [ADR-003: PostgreSQL Relational Database](architecture/adr/ADR-003-postgresql.md)
- [ADR-004: SQLAlchemy 2.0 + Alembic](architecture/adr/ADR-004-sqlalchemy-alembic.md)
- [ADR-005: ElevenLabs Provider Abstraction](architecture/adr/ADR-005-elevenlabs-provider-abstraction.md)
- [ADR-006: Qiskit Aer + PennyLane Simulation](architecture/adr/ADR-006-qiskit-pennylane.md)
- [ADR-007: Vercel + Render PaaS Deployment](architecture/adr/ADR-007-vercel-render.md)
- [ADR-008: Monorepo Architecture](architecture/adr/ADR-008-monorepo.md)
- [ADR-009: TanStack Query (Server) + Zustand (UI)](architecture/adr/ADR-009-tanstack-query-zustand.md)
- [ADR-010: Rejection of Microservices](architecture/adr/ADR-010-no-microservices.md)

---

## 1. Executive Architectural Overview

Bloop is an intermediate-level full-stack web application that unifies commercial-grade AI Text-to-Speech synthesis with an educational, research-oriented Quantum Intelligence laboratory.

The system is constructed upon three non-negotiable architectural tenets:
1. **Clean Layered Separation:** Presentation, API routing, business services, data repositories, and hardware/provider abstractions remain strictly decoupled.
2. **The Decoupling Invariant:** The core speech synthesis pipeline operates with 100% independence from the quantum layer. Quantum simulation latencies, errors, or timeouts can never degrade or block speech synthesis.
3. **The Dynamic Voice Architecture:** Zero fabricated voice IDs, fake names, or hardcoded vendor voice catalogues exist within application source code. All voices are retrieved, validated, and injected dynamically.

---

## 2. High-Level System Topology (C4 Container View)

```
                                  ┌───────────────────────────────┐
                                  │         User Browser          │
                                  │ (Desktop, Tablet, Mobile Web) │
                                  └───────────────┬───────────────┘
                                                  │
                                          HTTPS / TLS 1.3
                                                  │
                                  ┌───────────────▼───────────────┐
                                  │          Vercel Edge          │
                                  │    React 19 + Vite SPA        │
                                  │   (Tailwind + Zustand + Tan)  │
                                  └───────────────┬───────────────┘
                                                  │
                                    REST APIs / JSON Envelope
                                    (Bearer JWT Authorization)
                                                  │
                                  ┌───────────────▼───────────────┐
                                  │       Render Web Service      │
                                  │       FastAPI (Python 3.12)   │
                                  │  (Pydantic v2 + SQLAlchemy 2) │
                                  └───┬───────────┬───────────┬───┘
                                      │           │           │
                     ┌────────────────┘           │           └─────────────────┐
                     ▼                            ▼                             ▼
       ┌───────────────────────────┐┌───────────────────────────┐┌───────────────────────────┐
       │     Render PostgreSQL     ││    Server Disk Storage    ││    ElevenLabs REST API    │
       │    Relational Metadata    ││  Chunked MP3 Audio Files  ││  Commercial AI Synthesis  │
       │ Users, Voices, Hist, Favs ││   HTTP 206 Partial Content││  https://api.elevenlabs.io│
       └───────────────────────────┘└───────────────────────────┘└───────────────────────────┘
                                                  │
                                  ┌───────────────▼───────────────┐
                                  │   Quantum Intelligence Core   │
                                  │ (Decoupled Simulation Engine) │
                                  │   Qiskit Aer 2.x + PennyLane  │
                                  └───────────────────────────────┘
```

---

## 3. Clean Architecture & Layered Module Boundaries

The backend application follows Clean Architecture principles, enforcing unidirectional dependency flow:

```
 Presentation Layer (React 19 Frontend)
         │
         ▼
 Routing / API Layer (FastAPI Routers: /api/v1/*)
         │
         ▼
 Service / Business Logic Layer (TTSService, VoiceService, AuthService, QuantumService)
         ├──► Provider Abstraction Layer (BaseTTSProvider -> ElevenLabsProvider, SimulationProvider)
         │
         ▼
 Data Access / Repository Layer (UserRepository, GenerationRepository, VoiceRepository, etc.)
         │
         ▼
 Persistence Layer (SQLAlchemy 2.0 ORM, Alembic Migrations, PostgreSQL 16 / SQLite)
```

### Layer Invariant Rules:
* **Routers** only parse requests, invoke service methods, and return standard JSON response envelopes. They contain zero direct database queries or vendor API calls.
* **Services** orchestrate business workflows, validate business logic boundaries, enforce tenant isolation, and handle error translation.
* **Repositories** encapsulate raw SQL / ORM operations. They never parse HTTP requests or communicate with third-party APIs.
* **Providers** implement the `BaseTTSProvider` interface. The core application interacts exclusively with the abstract provider interface, never binding to ElevenLabs SDK specifics.

---

## 4. The Decoupled Architecture Invariant

The core Text-to-Speech synthesis pipeline and the Quantum Intelligence laboratory reside in independent execution paths:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           INDEPENDENT MODULE PATHS                          │
│                                                                             │
│  [HTTP Request]                                                             │
│         │                                                                   │
│         ├──► /api/v1/tts ────────► TTSService ─────► ElevenLabs / Sim ──► Audio (OK)
│         │                                                                   │
│         └──► /api/v1/quantum/* ──► QuantumService ─► Qiskit / Penny ──► Q-Insight
│                                                                             │
│  * Failure in QuantumService throws isolated QUANTUM_EXECUTION_ERROR.       │
│  * Core TTS pipeline remains 100% operational regardless of quantum state.  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Decoupling Rules:
1. **No Shared Blocking Threads:** Quantum simulations run in dedicated compute contexts with strict shot limits ($\le 1024$) and qubit limits ($\le 8$).
2. **Zero Runtime Dependency:** No TTS endpoint requires a quantum calculation to complete synthesis.
3. **Fault Containment:** If Qiskit or PennyLane encounters a simulator error or memory limit, the exception is caught within `QuantumService`, logged with a stack trace, and returned as an isolated error envelope without affecting server health.

---

## 5. Dynamic Voice Architecture & Ingestion Flow

Bloop contains **zero hardcoded ElevenLabs voice IDs**. All voices are treated as dynamic metadata records linked to ISO language locales.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DYNAMIC VOICE INGESTION MODES                       │
│                                                                             │
│  Mode 1: UI Modal        ──► POST /api/v1/voices ──────────┐                │
│                                                            │                │
│  Mode 2: Config File     ──► voices_config.json ───────────┼──► VoiceService│
│                              POST /api/v1/voices/reload    │          │     │
│                                                            │          ▼     │
│  Mode 3: Simulation Mode ──► Offline Synthetic Provider ───┘    Database     │
│                              (When API key is unconfigured)     Voice Table │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Dynamic Voice Workflow:
1. **Database Registry:** The `voices` table stores `voice_id`, `name`, `language_code`, `gender`, `provider`, and `is_active`.
2. **Language Relationship:** Languages (`languages` table) dictate compatible voices. Querying `GET /api/v1/voices?language_code=en-US` dynamically returns only active voices mapped to `en-US`.
3. **Runtime Ingestion:**
   * **UI Modal:** Users can inject custom ElevenLabs voice IDs directly in the frontend.
   * **Configuration File:** System operators can define voice mappings in `backend/voices_config.json`. On startup (or via `/api/v1/voices/reload-config`), `VoiceService` upserts these voices into the registry.
4. **Zero-Config Simulation Provider:** When `ELEVENLABS_API_KEY` is not present, `TTSService` automatically routes synthesis to `SimulationTTSProvider`. This provider generates valid audio waveforms locally, allowing complete end-to-end testing without external API costs.

---

## 6. Audio Storage & HTTP Range Streaming Architecture

Synthesized audio files are stored on server-side disk storage and delivered via HTTP `Range` streaming:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          AUDIO STREAMING ARCHITECTURE                       │
│                                                                             │
│  Browser <audio> ──[GET /api/v1/tts/audio/{file}]──► FastAPI Streaming Route │
│                           Range: bytes=0-1048575                            │
│                                                            │                │
│  Browser Player ◄──[HTTP 206 Partial Content]──────────────┘                │
│                     Content-Range: bytes 0-1048575/3145728                  │
│                     Content-Type: audio/mpeg                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Storage Principles:
* **Directory Structure:** Audio files are stored under `backend/app/storage/audio/`.
* **Collision-Resistant Naming:** Audio files use deterministic, collision-resistant UUID filenames (`bloop-{uuid4}.mp3`).
* **HTTP 206 Partial Content:** The audio endpoint parses `Range` headers, seeks the file stream, and yields chunked byte ranges. This enables instant scrubbing, pausing, and seeking without buffering the entire file.
* **Download Endpoint:** A separate endpoint (`/api/v1/tts/download/{filename}`) serves the file with `Content-Disposition: attachment; filename="bloop-speech-{id}.mp3"`.

---

## 7. Database Topology & Multi-Tenant Data Isolation

The database layer utilizes **SQLAlchemy 2.0** with **Alembic** migrations:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            RELATIONAL ENTITY GRAPH                          │
│                                                                             │
│         ┌───────────────┐ 1       * ┌────────────────────┐                  │
│         │     users     ├───────────┤ speech_generations │                  │
│         └───┬───────┬───┘           └─────────┬──────────┘                  │
│             │ 1     │ 1                       │ 1                           │
│             │       │                         │                             │
│             ▼ *     ▼ 1                       ▼ *                           │
│  ┌──────────────┐ ┌──────────────────┐      ┌───────────┐                   │
│  │  favorites   │ │ user_preferences │      │ languages │                   │
│  └──────────────┘ └──────────────────┘      └─────┬─────┘                   │
│                                                   │ 1                       │
│         ┌─────────────────────┐                   ▼ *                       │
│         │ quantum_experiments │             ┌───────────┐                   │
│         │ (Execution Logs)    │             │  voices   │                   │
│         └─────────────────────┘             └───────────┘                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Per-User Data Isolation Contract:
* Every user-specific table (`speech_generations`, `favorites`, `user_preferences`) maintains a mandatory foreign key constraint to `users.id`.
* The repository layer enforces tenant boundaries:
  ```python
  query = select(SpeechGeneration).where(
      SpeechGeneration.user_id == current_user.id
  )
  ```
* Direct object lookups (`/history/{id}`) verify ownership before returning data or deleting audio files. Cross-tenant access attempts immediately return HTTP 403 / 404.

---

## 8. Quantum Intelligence Engine Architecture

The Quantum layer consists of 5 modular engines operating under `backend/app/quantum/`:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       QUANTUM INTELLIGENCE ARCHITECTURE                     │
│                                                                             │
│  1. Text Classifier     ──► Qiskit Aer (VQC + Hilbert Angle Encoding)       │
│  2. Emotion QNN         ──► PennyLane default.qubit (Pauli-Z Expectations)  │
│  3. Semantic Kernel     ──► Qiskit Aer (Transition Fidelity Inversion)      │
│  4. Circuit Sandbox     ──► Qiskit Aer + Depolarizing Error Noise Model     │
│  5. Empirical Benchmark ──► Scikit-Learn (Logistic) vs Qiskit VQC           │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Engine Specifications:
1. **Text Classifier (`text_classifier.py`):** Extracts lexical diversity, word length, and vowel distribution; projects them to $[0, \pi]$; executes a 4-qubit Variational Quantum Classifier (VQC) with CNOT entangling gates on `AerSimulator`.
2. **Emotion QNN (`emotion_qnn.py`):** Utilizes PennyLane's `default.qubit` to evaluate 4 affective wires (Joy, Sadness, Anger, Neutral). Computes Shannon entanglement entropy $H = -\sum p_i \log_2(p_i)$ and derives explainable speech tuning parameters (speed multiplier, pitch variance).
3. **Semantic Kernel (`semantic_kernel.py`):** Computes quantum transition fidelity $|⟨\phi(A)|\psi(B)⟩|^2$ between two feature states using an inversion circuit $U^\dagger(B) U(A) |0\rangle$.
4. **Circuit Sandbox (`circuit_lab.py`):** Compiles arbitrary gate sequences (H, X, Y, Z, Rx, Ry, Rz, CNOT, CZ, SWAP); simulates ideal or noisy hardware decoherence; returns ASCII diagrams and OpenQASM 2.0.
5. **Empirical Benchmark (`benchmarks.py`):** Trains Scikit-Learn Logistic Regression alongside Qiskit VQC on a controlled dataset; measures Accuracy, F1-score, and wall-clock execution latency without false claims of quantum advantage.

---

## 9. Security Architecture & Boundary Controls

| Security Vector | Implementation Mechanism |
| :--- | :--- |
| **Secret Protection** | `ELEVENLABS_API_KEY`, `SECRET_KEY`, and `DATABASE_URL` are stored exclusively in server environment variables. Client bundles contain zero secrets. |
| **Password Storage** | Cryptographically salted hashes generated using `bcrypt` (Passlib). Plain-text passwords never touch disk or logs. |
| **Authentication** | Stateless JWT tokens with HMAC-SHA256 signature, 24-hour expiration, and strict bearer verification. |
| **CORS Policy** | FastAPI CORS middleware restricted to configured frontend origins (e.g. `localhost:3000`, `bloop.vercel.app`). Wildcard origins (`*`) are prohibited in production. |
| **Input Validation** | Pydantic v2 schemas reject malformed payloads, out-of-range text lengths ($<1$ or $>2,500$ chars), and invalid ISO language codes at the perimeter. |
| **Provider Isolation** | ElevenLabs API failures or timeouts are trapped server-side and translated to safe JSON errors, preventing internal infrastructure leaks. |

---

## 10. Production Cloud Deployment Architecture

```
                             ┌─────────────────────────┐
                             │       Vercel Edge       │
                             │  React 19 + Vite (SPA)  │
                             │   https://bloop.app     │
                             └────────────┬────────────┘
                                          │
                                       HTTPS
                                          │
                             ┌────────────▼────────────┐
                             │    Render Web Service   │
                             │   FastAPI + Uvicorn     │
                             │ https://api.bloop.app   │
                             └──────┬───────────┬──────┘
                                    │           │
                      ┌─────────────┘           └──────────────┐
                      ▼                                        ▼
           ┌───────────────────────┐              ┌─────────────────────────┐
           │   Render PostgreSQL   │              │   ElevenLabs Cloud API  │
           │  Managed Database 16  │              │  https://api.elevenlabs │
           └───────────────────────┘              └─────────────────────────┘
```

* **Backend:** Render Web Service executing `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT` with auto-migration `alembic upgrade head`.
* **Frontend:** Vercel static edge hosting with `vercel.json` rewrite routing all requests to `index.html`.
* **Probes:** Render uptime monitoring configured to ping `GET /api/v1/health` every 30 seconds.
