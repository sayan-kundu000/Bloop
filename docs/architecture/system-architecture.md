# Bloop — Full-Stack System Architecture Specification

**Document Identifier:** BLOOP-ARCH-SPEC-V1  
**Project:** Bloop — AI Text-to-Speech & Quantum Intelligence Platform  
**Target Milestone:** Intermediate-Level Architecture Baseline  
**Status:** Approved Master Architecture  
**Authority:** Bloop Master Prompt, Prompt 01 (PRS), and Prompt 02  

---

## 1. Executive Architectural Summary & High-Level Vision

Bloop is an intermediate-level, production-style full-stack application designed to unify high-fidelity commercial AI Text-to-Speech synthesis with an educational, research-grade Quantum Intelligence laboratory.

```
                         BLOOP
                           │
              ┌────────────┴────────────┐
              │                         │
       Core TTS Platform        Quantum Intelligence
              │                         │
              ▼                         ▼
        React Frontend             Quantum Lab
              │                         │
              └────────────┬────────────┘
                           │
                      REST / JSON
                           │
                           ▼
                    FastAPI Backend
                           │
          ┌────────────────┼─────────────────┐
          │                │                 │
          ▼                ▼                 ▼
      PostgreSQL       ElevenLabs       Quantum Engine
```

The system is architected around two core domains:
1. **Core AI Text-to-Speech Platform:** Fast, reliable, production-ready speech synthesis mediated by a Python FastAPI backend communicating securely with the ElevenLabs REST API.
2. **Quantum Intelligence Platform:** A dedicated, isolated side-car computational engine running on Qiskit Aer and PennyLane for text feature extraction, quantum classification, affective emotion modeling, semantic state fidelity, circuit experimentation, and empirical benchmarking.

---

## 2. Core Architectural Principles

### 2.1 The Decoupled Architecture Invariant (Core TTS First)
The fundamental architectural law of Bloop is that **basic Text-to-Speech synthesis must never depend on the quantum engine**:
- Core TTS path: `Text -> Validation -> Language -> Voice -> FastAPI -> ElevenLabs -> Audio Stream`.
- Quantum path: `Text / Features -> Quantum Intelligence -> Qiskit / PennyLane Simulation -> Result`.
- If a quantum simulation fails, encounters decoherence error, exceeds CPU limits, or times out, the core TTS platform remains 100% operational.
- Quantum recommendations (e.g., emotion-derived pitch/speed multipliers) act strictly as optional side-car advisory data that the user may optionally apply.

### 2.2 Dynamic Voice Architecture (Zero Hardcoded Voices)
- **Zero Fabricated Voice Rule:** No fake voice IDs, mock names, or hardcoded vendor voice catalogues exist in production application source code.
- All voices are treated as dynamic metadata records linked to ISO language codes.
- Voices are ingested at runtime through three supported channels:
  1. Frontend UI Modal (user provides active ElevenLabs Voice ID).
  2. Server Configuration (`backend/voices_config.json`).
  3. REST API (`POST /api/v1/voices`).
- When `ELEVENLABS_API_KEY` is not present, the system automatically falls back to an offline simulation provider generating synthetic tones, enabling 100% test pass rates without vendor credentials.

### 2.3 Audio Storage Separation Principle
- PostgreSQL persists **only relational metadata** (user ID, prompt text, character count, duration, voice ID, provider, filename, timestamp).
- Binary audio files are stored in server-side disk storage (`backend/app/storage/audio/`) using collision-resistant UUIDs (`bloop-{uuid4}.mp3`).
- Audio playback utilizes **HTTP 206 Partial Content Range streaming**, enabling low-latency seeking, instant scrubbing, and sub-second startup without client-side buffering delays.

### 2.4 Intermediate-Level Engineering Simplicity
The architecture avoids unnecessary enterprise bloat:
- **No Microservices:** Single unified FastAPI backend.
- **No Distributed Message Brokers:** In-process async execution instead of Kafka, Celery, or RabbitMQ.
- **No Kubernetes/Service Mesh:** Streamlined deployment on Render and Vercel.
- **Single Authoritative Database:** One PostgreSQL database housing all multi-tenant tables.

---

## 3. High-Level System Topology (C4 Container View)

```mermaid
flowchart TD
    subgraph Client [Client Presentation Layer]
        User[User Browser / Device]
        VercelSPA[Vercel Edge Network\nReact 19 + TypeScript + Vite SPA\nTailwind CSS + Zustand + TanStack Query]
        User -->|HTTPS / TLS 1.3| VercelSPA
    end

    subgraph BackendGateway [Backend Application Layer - Render]
        FastAPIApp[Render Web Service\nFastAPI 0.115+ / Uvicorn ASGI Server\nPython 3.11+]
        VercelSPA -->|HTTPS REST JSON\nBearer JWT Auth| FastAPIApp
    end

    subgraph StorageLayer [Persistence & Local Storage Layer - Render]
        PG[(Render Managed PostgreSQL 16\nUsers, Voices, History, Favorites)]
        AudioDisk[Server Disk Storage\nChunked MP3 Audio Files\nHTTP 206 Range Delivery]
        FastAPIApp -->|SQLAlchemy 2.0 ORM\nAlembic Migrations| PG
        FastAPIApp -->|Chunked File I/O| AudioDisk
    end

    subgraph ExternalProviders [External Provider Layer]
        ElevenLabs[ElevenLabs Cloud REST API\nv1/text-to-speech/{voice_id}\nCommercial AI Voice Synthesis]
        FastAPIApp -->|HTTPS / HTTPX Async\nProtected API Key| ElevenLabs
    end

    subgraph QuantumSubsystem [Quantum Intelligence Layer - In-Process]
        QuantumCore[Quantum Intelligence Core\nQiskit Aer 0.15+ & PennyLane 0.38+\nText VQC, Emotion QNN, Semantic Kernel]
        FastAPIApp -->|Isolated Async Calls\nStrict Qubit/Shot Limits| QuantumCore
    end
```

---

## 4. Layered Module Boundaries

Bloop strictly enforces unidirectional dependencies between Clean Architecture layers:

```
Presentation Layer (React 19 SPA)
        │
        ▼
Routing / API Layer (FastAPI Routers: /api/v1/*)
        │
        ▼
Service Layer (TTSService, VoiceService, AuthService, HistoryService, QuantumService)
        ├──► Provider Abstraction (BaseTTSProvider -> ElevenLabsProvider, SimulationProvider)
        │
        ▼
Repository Layer (UserRepository, VoiceRepository, SpeechGenerationRepository, etc.)
        │
        ▼
Persistence Layer (SQLAlchemy 2.0 ORM, Alembic Migrations, PostgreSQL 16)
```

### Boundary Responsibilities

| Layer | Primary Responsibilities | Strict Non-Responsibilities |
| :--- | :--- | :--- |
| **Boundary 01: Frontend** | UI rendering, user interaction, client-side input validation, counters, audio player controls, TanStack Query mutations/caching, Zustand UI state. | Never touches ElevenLabs API keys, database credentials, direct vendor APIs, or authoritative validation. |
| **Boundary 02: API Layer** | HTTP routing, request parsing, Pydantic v2 schema validation, dependency injection (JWT auth, DB session), HTTP status code mapping, JSON envelope formatting. | Never contains SQL queries, provider implementation logic, or quantum circuit construction. |
| **Boundary 03: Service Layer** | Core business logic orchestration, tenant ownership checks, coordinating repositories and providers, error normalization. | Never parses HTTP headers, reads raw SQL cursors, or renders UI. |
| **Boundary 04: Repository Layer** | Encapsulated database operations (CRUD, queries, pagination, multi-parametric filtering, transactions). | Never performs HTTP requests, third-party vendor calls, or presentation formatting. |
| **Boundary 05: Provider Layer** | Concrete implementations of `BaseTTSProvider` (ElevenLabs API integration, simulation audio synthesis). | Never interacts with database models or frontend state. |
| **Boundary 06: Quantum Layer** | Feature vector scaling, Hilbert angle mappings, Qiskit circuits, PennyLane QNN nodes, Aer simulations, classical benchmark baselines. | Never blocks or couples into core TTS synthesis requests. |

---

## 5. Master Module Map

```
BLOOP
│
├── Frontend (React 19 + TypeScript + Vite)
│   ├── auth/          # Authentication pages, login/register modals, JWT storage
│   ├── tts/           # Text workspace, live counters, voice/language selectors, AudioPlayer
│   ├── dashboard/     # User analytics, generation activity, quick access
│   ├── history/       # Paginated generation history, search bar, multi-filters
│   ├── favorites/     # Bookmarked generations, quick playback, custom notes
│   ├── profile/       # User preferences (default language/voice, theme)
│   ├── quantum/       # Quantum Lab: Text Classifier, Emotion QNN, Semantic Kernel, Circuit Lab, Benchmark
│   ├── components/    # Reusable UI primitives (Button, Modal, Input, Badge, Toast)
│   ├── hooks/         # Custom React hooks (useAudioPlayer, useTTSWorkspace, useDebounce)
│   ├── stores/        # Zustand stores (authStore, uiStore, playerStore)
│   ├── api/           # Axios/Fetch client, TanStack Query hooks, API contracts
│   └── types/         # TypeScript interfaces mirroring backend schemas
│
├── Backend (Python 3.11+ / FastAPI)
│   ├── api/           # API Routers (/api/v1/health, auth, tts, voices, languages, history, favorites, quantum)
│   ├── core/          # Application configuration, Pydantic Settings, security (JWT/bcrypt), logging
│   ├── db/            # Database session factory, SQLAlchemy base model, Alembic migrations
│   ├── models/        # Declarative ORM models (User, Voice, Language, SpeechGeneration, Favorite, Preference)
│   ├── schemas/       # Pydantic v2 request/response schemas, JSON envelopes
│   ├── repositories/  # Database access objects (UserRepository, VoiceRepository, GenerationRepository, etc.)
│   ├── services/      # Business orchestrators (TTSService, AuthService, VoiceService, QuantumService)
│   ├── providers/     # BaseTTSProvider, ElevenLabsProvider, SimulationTTSProvider
│   ├── quantum/       # Text Classifier, Emotion QNN, Semantic Kernel, Circuit Lab, Benchmarks
│   ├── storage/       # Disk storage manager for generated MP3 files, HTTP 206 byte-range streamer
│   └── main.py        # FastAPI application bootstrap, CORS middleware, global exception handlers
│
├── Infrastructure & Persistence
│   ├── PostgreSQL     # Managed relational database (Users, Metadata, Relations)
│   ├── ElevenLabs     # Commercial cloud TTS provider
│   └── Disk Storage   # Server directory for chunked audio streaming
│
└── Deployment & CI/CD
    ├── GitHub         # Version control, CI test runner, automatic deploy triggers
    ├── Render         # Web service hosting FastAPI + Managed PostgreSQL
    └── Vercel         # Edge CDN hosting React 19 SPA
```

---

## 6. Unidirectional Dependency Rule

Bloop strictly enforces unidirectional module dependencies. Cyclic dependencies between modules are prohibited:

```
[API Endpoints / Routers]
           │
           ▼
   [Business Services]
      │           │
      ▼           ▼
[Repositories]  [Providers / Quantum Engines]
      │           │
      ▼           ▼
[Database ORM]  [External APIs / Simulators]
```

### Invariant Rules:
1. **No Circular Imports:** If Service A and Service B require shared functionality, the common logic is extracted into a dedicated helper, utility, or repository.
2. **Repositories Never Import Services:** Repositories only receive and return database entities and scalars.
3. **Routers Never Import Repositories Directly:** All data retrieval passes through the Service layer to ensure authorization and validation rules are executed.
4. **Schemas Are Pure Data Contracts:** Pydantic schemas never import database models or services.

---

## 7. Requirement-to-Architecture Traceability Matrix

Every requirement defined in Prompt 01 (PRS) maps directly to concrete architectural components:

| Requirement ID | Requirement Title | Architectural Component | Implementing Modules |
| :--- | :--- | :--- | :--- |
| **BR-001 / FR-006** | High-Fidelity Speech Generation | Backend TTS Pipeline & Provider | `api/v1/endpoints/tts.py`, `TTSService`, `ElevenLabsProvider` |
| **BR-002 / FR-001** | Text Input & Live Counters | Frontend TTS Workspace | `frontend/src/components/tts/TextWorkspace.tsx`, `useCounters` |
| **FR-002 / FR-003** | Text Length & Empty Validation | Dual-Layer Validation | `frontend/src/utils/validation.ts`, `schemas/tts.py` |
| **FR-004** | Multilingual Locales | Language Domain Service | `api/v1/endpoints/languages.py`, `LanguageRepository` |
| **BR-003 / FR-005** | Dynamic Voice Architecture | Voice Registry & Ingestion | `api/v1/endpoints/voices.py`, `VoiceService`, `VoiceRepository` |
| **FR-007 / FR-008** | Audio Playback & Download | Audio Streaming & Storage Engine | `storage/audio_manager.py`, `AudioPlayerBar.tsx` |
| **BR-005 / FR-009** | User Authentication & JWT | Security & Auth Service | `core/security.py`, `AuthService`, `api/v1/endpoints/auth.py` |
| **FR-011 / FR-012** | Speech History & Multi-Filter | History Service & Paginated Repo | `HistoryService`, `SpeechGenerationRepository`, `HistoryPage.tsx` |
| **FR-013** | Favorites & Bookmarks | Favorites Service & Repo | `FavoriteService`, `FavoriteRepository`, `FavoritesPage.tsx` |
| **FR-014** | User Preferences | Preferences Domain | `UserPreferenceRepository`, `ProfilePage.tsx` |
| **QR-001 / FR-015** | Quantum Text Classification | Qiskit VQC Engine | `backend/app/quantum/text_classifier.py`, `QuantumService` |
| **QR-002 / FR-016** | Quantum Emotion QNN | PennyLane Affective Engine | `backend/app/quantum/emotion_qnn.py`, `QuantumService` |
| **QR-003 / FR-017** | Quantum Semantic Kernel | Qiskit State Fidelity Inversion | `backend/app/quantum/semantic_kernel.py`, `QuantumService` |
| **QR-004 / FR-018** | Interactive Circuit Lab | Qiskit Aer Sandbox | `backend/app/quantum/circuit_lab.py`, `CircuitLabPage.tsx` |
| **QR-005 / FR-019** | Classical vs Quantum Benchmark | Empirical Benchmarking Engine | `backend/app/quantum/benchmarks.py`, `BenchmarkPage.tsx` |
| **FR-020 / NFR-006** | System Health Observability | Health Probe Endpoint | `api/v1/endpoints/health.py` |
| **BR-008 / DR-001** | Cloud Production Readiness | Cloud PaaS Infrastructure | `render.yaml`, `frontend/vercel.json`, `docs/architecture/deployment-architecture.md` |

---

## 8. Implementation Sequencing

The architecture is partitioned into 16 sequential implementation phases, ensuring that dependencies are established prior to dependent features:

```
01. Foundation & Repository Baseline (Monorepo, configs, docs)
        ↓
02. Database Baseline (SQLAlchemy 2.0, Alembic migration scaffold)
        ↓
03. FastAPI Core Engine (Bootstrap, CORS, exception handlers)
        ↓
04. REST API Contracts & Envelope Specs (Pydantic v2 schemas)
        ↓
05. Text Input Validation & Sanitization Engine
        ↓
06. Dynamic Language & Voice Architecture (Voice registry & ingestion)
        ↓
07. ElevenLabs Provider & Offline Simulation Fallback
        ↓
08. Audio Storage & HTTP 206 Partial Content Streamer
        ↓
09. Authentication, Password Hashing & JWT Authorization
        ↓
10. Multi-Tenant User Data Isolation & Preferences
        ↓
11. React 19 Frontend Workspace & Interactive Audio Player
        ↓
12. History, Multi-Parametric Search, Filtering & Bookmarking UI
        ↓
13. Quantum Intelligence Laboratory (Qiskit VQC, PennyLane QNN)
        ↓
14. Security Perimeter, Rate Limiting & Input Sanitization
        ↓
15. End-to-End Automated Testing & Mocked Verification Suites
        ↓
16. Production Cloud Deployment (Render Web Service + PostgreSQL + Vercel Edge)
```

---

## 9. Architecture Quality Gate Checklist

The Bloop architecture satisfies all 10 Architectural Quality Gates:

- [x] **Q1: Clean Frontend/Backend Communication?** Yes. Strictly typed REST APIs with standard JSON envelopes and Bearer JWT authorization.
- [x] **Q2: Protected Credentials?** Yes. `ELEVENLABS_API_KEY` and database credentials exist exclusively on the server in `.env`.
- [x] **Q3: Isolated User Data?** Yes. Enforced by mandatory `user_id` foreign keys and repository-level query constraints.
- [x] **Q4: Database Migration Path?** Yes. Managed via SQLAlchemy 2.0 and versioned Alembic scripts.
- [x] **Q5: Non-Blocking Quantum Subsystem?** Yes. Decoupled Architecture Invariant guarantees zero blocking impact on core TTS.
- [x] **Q6: Extensible Voice Architecture?** Yes. Dynamic ingestion via UI modal, JSON config, and REST API; zero hardcoded vendor voice IDs.
- [x] **Q7: Single Render Web Service?** Yes. All backend services, including quantum engines, run in a single FastAPI application.
- [x] **Q8: Single Vercel Application?** Yes. React 19 SPA compiles to static assets hosted on Vercel's Edge Network.
- [x] **Q9: Independent Testability?** Yes. Repositories test against SQLite; Providers test with `SimulationTTSProvider`; Quantum engines test with synthetic vectors.
- [x] **Q10: Accessible to New Engineers?** Yes. Layered Clean Architecture with comprehensive documentation and no convoluted enterprise overhead.
