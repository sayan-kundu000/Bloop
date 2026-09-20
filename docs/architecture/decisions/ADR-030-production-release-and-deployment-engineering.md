# ADR-030: Security, Production Deployment, Render + Vercel & Final Release Engineering

## Status
Accepted

## Context
With Prompts 01–27 complete, Bloop represents a full-stack AI Text-to-Speech platform featuring dynamic voice capability discovery, authenticated audio generation, user history/favorites curation, and an isolated side-car Quantum Intelligence layer (Qiskit Aer, PennyLane, hybrid QNN, semantic kernel, and multi-category benchmarking).

Prompt 28 establishes the **Final Production-Readiness Gate**:
1. Verifying that the architecture remains intermediate-level, decoupled, and free of unnecessary enterprise infrastructure (no Kubernetes, Kafka, Redis clusters, or service meshes).
2. Conducting an end-to-end security audit across authentication, authorization, CORS, input validation, audio delivery, provider secrets, and HTTP security headers.
3. Establishing automated GitHub CI workflows for backend tests, migrations, frontend tests, and production build checks.
4. Defining deployment blueprints for Render (FastAPI Web Service + Render PostgreSQL) and Vercel (React 19 + TypeScript + Vite SPA).
5. Ensuring 100% test pass rate across unit, security, integration, smoke, and quantum suites.
6. Establishing authoritative copyright (`Copyright © 2026 Bloop. All rights reserved.`) and explicitly confirming that no license file is created.

## Decision

### 1. Authoritative Monorepo & Decoupled Topology
We maintain the decoupled monorepo architecture:
- **Core TTS Dependency Chain**:
  `React (Vercel) -> FastAPI (Render) -> SpeechService -> ElevenLabsProvider -> Audio Delivery`
- **Quantum Subsystem Isolation**:
  Quantum Intelligence operates as an optional side-car (`QuantumService -> Qiskit / PennyLane`). If quantum execution times out or fails, the core TTS platform remains 100% available without disruption.
- **Dynamic Voice Discovery**:
  Maintains provider-independent voice capabilities validated through `CapabilityService`. No hardcoded or fabricated voice catalogues are permitted.

### 2. Security Hardening & Headers
- **Authentication**: Salted password hashing (Argon2id/Bcrypt), secure JWT access tokens, opaque login error messages preventing user enumeration, and database-level unique email enforcement.
- **Authorization**: Mandatory `user_id` ownership verification across all user-owned domain resources (generations, speech history, favorites, quantum experiments).
- **HTTP Security Headers**:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `X-XSS-Protection: 1; mode=block`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Permissions-Policy: camera=(), microphone=(), geolocation=()`
  - `Strict-Transport-Security: max-age=31536000; includeSubDomains` (enforced when `APP_ENV == "production"`)
- **CORS Enforcement**: Strictly driven by `CORS_ORIGINS`. Wildcard `*` is prohibited at application startup in production.
- **Input & Payload Guardrails**: Pydantic v2 schemas reject malformed inputs before reaching services; `PayloadLimitMiddleware` rejects payloads exceeding 2MB (HTTP 413).

### 3. Production Deployment Topography
- **Render Web Service & PostgreSQL (`render.yaml`)**:
  - Web service running Uvicorn: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`.
  - Build command automatically applies migrations: `pip install -r backend/requirements.txt && alembic upgrade head`.
  - Managed PostgreSQL 16 database connection via environment `DATABASE_URL`.
  - Liveness and health monitoring via `/api/v1/health`.
- **Vercel Frontend (`frontend/vercel.json`)**:
  - Static distribution deployed from `frontend/dist`.
  - SPA routing rewrite `/(.*)` -> `/index.html`.
  - Edge security headers attached to all routes.
  - Public API base URL configured via `VITE_API_BASE_URL`.

### 4. Automated Testing & Verification Gates
- **Backend Tests (Pytest)**:
  - 151/151 quantum tests passing across text, emotion, semantic, laboratory, and hybrid benchmarking engines.
  - 12/12 core TTS, auth, and dynamic voice regression tests passing.
  - 6/6 security hardening tests passing.
  - 2/2 smoke test suites passing, including the full end-to-end user release journey.
- **Frontend Tests (Vitest)**:
  - 148/148 unit and integration tests passing across 16 test files (100% pass rate).
- **Static Analysis & Build**:
  - TypeScript static verification: 0 errors (`tsc -b`).
  - Vite production build completes cleanly.

### 5. Copyright & License Invariant
- Project documentation and source files display:
  `Copyright © 2026 Bloop. All rights reserved.`
- In strict adherence to Prompt 28 §40, **no license file** (`LICENSE`, `LICENSE.md`, `LICENSE.txt`) is created, and the legacy MIT license file has been deleted.

## Consequences

### Positive
- Production deployment is reproducible, automated, and decoupled.
- Defense-in-depth security mitigates common web vulnerabilities (XSS, CSRF, clickjacking, MIME-sniffing, credential enumeration).
- Automated CI pipeline on GitHub enforces migration checks, backend tests, frontend tests, and production build validation before deployment.
- Zero data fabrication: honest empirical benchmarking, real dynamic voices, and transparent classical CPU speedups.

### Negative
- Quantum circuit simulation is bounded to classical CPU resource limits ($N \le 8$ qubits, shots $\le 8192$), which is appropriate and deliberate for this intermediate-level platform.
