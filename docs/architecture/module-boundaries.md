# Bloop — Module Boundaries & Interface Contracts

**Document Identifier:** BLOOP-BOUNDARIES-V2  
**Status:** Canonical Implementation Contract  
**Authority:** Master, Prompt 02, Prompt 03, Prompt 04, Prompt 05  

---

## 1. Architectural Layering & Separation of Concerns

Bloop strictly enforces unidirectional dependencies between Clean Architecture layers. Cross-layer violations are strictly prohibited.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MODULE BOUNDARY HIERARCHY                          │
├───────────────────────┬─────────────────────────────────────────────────────┤
│ 1. Presentation Layer │ React 18, TypeScript, Tailwind, TanStack Query, UI  │
│ 2. API Perimeter      │ FastAPI APIRouters, Pydantic v2 Schemas, Dependency │
│ 3. Service Layer      │ TTSService, VoiceService, AuthService, QuantumService│
│ 4. Provider Layer     │ TTSProvider, ElevenLabsProvider, SimulationTTSProvider│
│ 5. Repository Layer   │ UserRepository, GenerationRepository, FavoriteRepo  │
│ 6. Persistence Layer  │ SQLAlchemy 2.x ORM, Alembic Migrations, PostgreSQL  │
│ 7. Quantum Subsystem  │ Qiskit Aer, PennyLane, Scikit-Learn Benchmarks      │
└───────────────────────┴─────────────────────────────────────────────────────┘
```

---

## 2. Layer Invariants & Rules

### 2.1 Route Layer (`backend/app/api/routes/`)
- **Owns:** HTTP request handling, Pydantic model validation, FastAPI dependency resolution, returning structured JSON.
- **Must NOT:** Contain database queries (`db.query(...)`), direct third-party HTTP requests (e.g. `httpx.post(...)`), or heavy quantum computations.
- **Input:** Request payloads parsed into Pydantic models.
- **Output:** Standardized `ApiResponse[T]` responses.

### 2.2 Service Layer (`backend/app/services/`)
- **Owns:** Core business logic coordination, input sanitization, invoking repositories, selecting TTS providers, calculating metrics.
- **Must NOT:** Import or depend on FastAPI HTTP requests, response headers, or status codes.
- **Input:** Primitive types or domain models.
- **Output:** Domain entities or structured DTOs.

### 2.3 Repository Layer (`backend/app/repositories/`)
- **Owns:** SQLAlchemy persistence operations: insert, update, query by ID, filter, pagination, soft-delete.
- **Must NOT:** Call external vendor APIs (ElevenLabs, Stripe, etc.) or execute quantum circuits.
- **Input:** SQLAlchemy Session + filter arguments or Pydantic schemas.
- **Output:** SQLAlchemy ORM model instances.

### 2.4 Provider Layer (`backend/app/providers/tts/`)
- **Owns:** External API communication with third-party speech engines (ElevenLabs) and local neural fallback simulations.
- **Must NOT:** Access the database, access HTTP route contexts, or manipulate user credentials directly.
- **Contract:** Inherits from abstract `TTSProvider`.

### 2.5 Quantum Layer (`backend/app/quantum/`)
- **Owns:** Variational Quantum Classifiers (VQC), PennyLane Quantum Neural Networks (QNN), Quantum Kernel Estimators, and Benchmarking pipelines.
- **Must NOT:** Import database models, FastAPI route handlers, or React components.
- **Isolation Guarantee:** Quantum intelligence is strictly additive. If quantum modules fail, core TTS speech synthesis is never blocked.
