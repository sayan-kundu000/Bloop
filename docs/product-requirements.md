# Bloop — Product Requirements Specification (PRS)

**Document Identifier:** BLOOP-PRS-V1  
**Project:** Bloop — AI Text-to-Speech & Quantum Intelligence Platform  
**Target Milestone:** Intermediate-Level MVP  
**Status:** Approved Product-Scope Contract  
**Authority:** Bloop Master Prompt & Product Requirements Architecture (Prompt 01)

---

## 1. Executive Summary & Vision

**Bloop** is a web-based artificial intelligence platform that converts user-provided text into natural, lifelike speech through a secure Python FastAPI backend and ElevenLabs integration, while providing an integrated **Quantum Intelligence Laboratory** for controlled experimentation with text representation, affective emotion classification, semantic state overlap, interactive quantum circuits, and classical-vs-quantum empirical benchmarking.

The system is architected around two connected but strictly decoupled layers:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Layer A: Core AI Text-to-Speech Platform                 │
│                                                                             │
│   User ──► Text Input ──► Language ──► Voice ──► FastAPI ──► ElevenLabs    │
│                                                                   │         │
│             Playback / Seek / Volume / Download ◄──── Audio Stream ◄──────┘ │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                   Layer B: Quantum Intelligence Platform                    │
│                                                                             │
│   Text / Features ──► Qubit Angle Encoding ──► Qiskit / PennyLane Simulators │
│                                                          │                  │
│       Empirical Benchmark / Insights ◄── Classical Baseline Comparison ◄────┘│
└─────────────────────────────────────────────────────────────────────────────┘
```

### The Decoupling Invariant
Layer B (Quantum Intelligence) must **never** make Layer A (Core TTS) dependent on quantum execution. If quantum simulation fails, times out, or is disabled, the core Text-to-Speech synthesis pipeline remains 100% operational.

---

## 2. Requirement Taxonomy & ID Strategy

All requirements within the Bloop project are assigned stable, traceable alphanumeric identifiers:

* **`BR-xxx`**: Business & Product Requirements
* **`FR-xxx`**: Functional Requirements (TTS, Backend, User Platform, Quantum, Security)
* **`NFR-xxx`**: Non-Functional Requirements (Security, Reliability, Maintainability, Usability, Performance, Observability)
* **`QR-xxx`**: Quantum Intelligence Requirements
* **`DR-xxx`**: Deployment & Infrastructure Requirements

---

## 3. Business & Product Requirements (BR)

| Requirement ID | Title | Description | Priority |
| :--- | :--- | :--- | :--- |
| **BR-001** | High-Fidelity Speech Generation | Provide natural, human-grade speech synthesis via ElevenLabs backend integration. | Critical (P1) |
| **BR-002** | Frictionless Web Experience | Responsive single-page application for text input, dynamic voice selection, audio playback, and instant downloads. | Critical (P1) |
| **BR-003** | Dynamic Voice Architecture | Strictly avoid hardcoding voice IDs or arbitrary catalogues; provide dynamic ingestion and validation of user-supplied voice IDs. | Critical (P1) |
| **BR-004** | Multilingual Locales | Dynamic support for standard ISO languages (`en-US`, `en-GB`, `es-ES`, `fr-FR`, `de-DE`, `hi-IN`). | High (P2) |
| **BR-005** | User Account & Data Ownership | Secure authentication allowing users to manage their private history, favorites, and UI preferences in complete isolation. | High (P2) |
| **BR-006** | Speech History & Bookmarks | Persistent recording of generation metadata (text, voice, duration, timestamp) with search, filter, and favorite features. | High (P2) |
| **BR-007** | Educational Quantum Intelligence | Dedicated experimentation lab demonstrating intermediate quantum computing concepts without unproven superiority claims. | Medium (P3) |
| **BR-008** | Cloud Production Readiness | Fully deployable on cloud infrastructure: FastAPI + PostgreSQL on Render, React frontend on Vercel. | Critical (P1) |

---

## 4. Functional Requirements (FR)

### 4.1 Category A: Core Text-to-Speech (FR-TTS)

#### FR-001: Text Input & Live Counters
* **Description:** The user interface must provide a dedicated text entry workspace with live calculation of character count, word count, and estimated audio duration.
* **Input:** Raw text string provided by user.
* **Processing:** Real-time client-side calculation; word count defined by whitespace boundaries; estimated duration calculated at average speech rate (~150 words per minute).
* **Output:** Visual counters displayed below the text input area.
* **Validation:** Enforce minimum length of 1 character (trimmed) and maximum length of 2,500 characters.

#### FR-002: Empty Text Rejection
* **Description:** The system must reject speech generation if text is empty, whitespace-only, or missing.
* **Behavior:** Generation button disabled in UI when empty; backend rejects requests with HTTP 422 / 400 and structured error code `EMPTY_TEXT`. External providers must never be invoked.

#### FR-003: Maximum Text Length Boundary Enforcement
* **Description:** The system must strictly enforce the maximum character limit (2,500 characters).
* **Behavior:** Frontend counter displays warning threshold and blocks submission past limit. Backend independently validates character count and rejects oversized requests with HTTP 422 / 400 `TEXT_TOO_LONG`.

#### FR-004: Language Selection
* **Description:** Users must be able to select from supported ISO language locales (`en-US`, `en-GB`, `es-ES`, `fr-FR`, `de-DE`, `hi-IN`).
* **Processing:** Selecting a language dynamically updates the list of compatible voices available in the voice selector.

#### FR-005: Dynamic Voice Architecture & Selector
* **Description:** The system must provide dynamic voice retrieval and selection decoupled from hardcoded ElevenLabs IDs.
* **Contract:** Voices are retrieved dynamically from the backend (`GET /api/v1/voices?language_code=...`). The system must support runtime injection of user-provided ElevenLabs voice IDs via UI modal, configuration file (`voices_config.json`), or REST API (`POST /api/v1/voices`).
* **Voice Scope Invariant:** Zero fabricated voice IDs or fake voice names hardcoded in production source code.

#### FR-006: Backend-Mediated Speech Synthesis
* **Description:** The FastAPI backend mediates all ElevenLabs synthesis requests.
* **Security:** Client requests pass text, language, and voice ID to `/api/v1/tts`. Backend attaches server-side `ELEVENLABS_API_KEY`, calls ElevenLabs, and handles binary audio response. Client never communicates directly with ElevenLabs.
* **Fallback:** When `ELEVENLABS_API_KEY` is unset or empty, the backend automatically invokes an offline simulation provider generating valid audio tones for local developer testing.

#### FR-007: Audio Playback & Interactive Controls
* **Description:** Once synthesized audio is returned, the frontend must render an interactive player.
* **Controls:** Play, Pause, Seeking scrubber bar, Current Time & Total Duration display, Volume slider with mute toggle, and Playback Speed selector (0.75x, 1.0x, 1.25x, 1.5x, 2.0x).
* **Streaming Support:** Backend audio endpoint (`/api/v1/tts/audio/{filename}`) must support HTTP 206 Partial Content / `Range` headers for smooth scrubbing.

#### FR-008: Audio File Download
* **Description:** Users must be able to download the generated audio file to their local machine.
* **Endpoint:** `GET /api/v1/tts/download/{filename}` delivering `Content-Disposition: attachment; filename="bloop-speech-{id}.mp3"`.

#### FR-009: Text Editing & Workspace Reset
* **Description:** Users must be able to quickly clear the workspace text or copy text from previous generations.

---

### 4.2 Category B: Backend Services & API Contracts (FR-API)

#### FR-010: RESTful API & JSON Envelope Contract
* **Description:** All backend endpoints must adhere to versioned REST standards (`/api/v1`) and return a standardized JSON envelope:
  * **Success:** `{"success": true, "data": { ... }, "message": "..."}`
  * **Error:** `{"success": false, "error": {"code": "ERROR_CODE", "message": "...", "details": ...}}`

#### FR-011: Pydantic Validation Layer
* **Description:** All incoming payloads must be strictly validated via Pydantic v2 schemas before execution. Any malformed input returns HTTP 422 with structured validation issues.

#### FR-012: Provider Abstraction Service
* **Description:** Synthesis logic must reside behind an abstract provider interface (`BaseTTSProvider`), separating business services from third-party vendor SDKs.

#### FR-013: Health & Diagnostics Endpoint
* **Description:** `GET /api/v1/health` must return service status, database connectivity status, provider configuration state (ElevenLabs vs. Simulation), and application version.

#### FR-014: Interactive OpenAPI Documentation
* **Description:** FastAPI must serve interactive Swagger UI at `/docs` and ReDoc at `/redoc` in non-production environments.

---

### 4.3 Category C: User Platform & Persistence (FR-USR)

#### FR-015: User Registration
* **Description:** Allow new users to create accounts using valid email and password (minimum 8 characters). Passwords must be hashed using bcrypt before database storage.

#### FR-016: User Authentication & JWT Session
* **Description:** Secure login endpoint (`POST /api/v1/auth/login`) returning a signed JSON Web Token (JWT). Frontend stores token securely and attaches `Authorization: Bearer <token>` to protected requests.

#### FR-017: User Profile & Preferences
* **Description:** Authenticated users can retrieve and update their profile and persistent preferences (default language, default voice, theme, default playback rate).

#### FR-018: Speech Generation History
* **Description:** Every successful speech generation by an authenticated user is persisted in PostgreSQL with metadata (text snippet, word count, character count, voice ID, language, duration, audio filename, timestamp).

#### FR-019: Bookmarked Favorites
* **Description:** Users can toggle bookmark status on any generation. Dedicated `GET /api/v1/favorites` retrieves all bookmarked items.

#### FR-020: History Search, Filter, Sort & Pagination
* **Description:** History listing supports:
  * Search: substring query matching against input text
  * Filter: filter by language code or voice ID
  * Sort: sort by creation date (ascending / descending)
  * Pagination: `page` and `page_size` parameters returning structured pagination metadata.

#### FR-021: Strict Data Isolation (Multi-User Privacy)
* **Description:** Database queries must automatically filter records by `user_id == current_user.id`. User A must never view, edit, or delete User B's history, audio files, or favorites.

---

### 4.4 Category D: Quantum Intelligence Platform (FR-QNT)

#### FR-022: Qiskit Statevector & Angle Encoding
* **Description:** Text features (length, lexical entropy, sentiment polarity, vowel frequency) are normalized to $[0, \pi]$ and encoded into qubit rotation angles $|\psi(x)\rangle = \bigotimes R_y(x_i) |0\rangle$.

#### FR-023: Variational Quantum Text Classifier (VQC)
* **Description:** Parameterized ansatz circuit with entangling CNOT layers executed on Qiskit Aer (`AerSimulator`). Output probabilities classify text style (Formal, Casual, Technical, Creative).

#### FR-024: Hybrid Quantum Neural Network (PennyLane Emotion QNN)
* **Description:** Hybrid QNN evaluating 4 affective wires (Joy, Sadness, Anger, Neutral) using Pauli-Z expectation values $\langle Z_i \rangle$.

#### FR-025: State Entanglement Entropy Calculation
* **Description:** Calculate multi-qubit state Shannon entanglement entropy $H = -\sum p_i \log_2(p_i)$ reflecting quantum superposition complexity.

#### FR-026: Explainable Voice Parameter Recommendation
* **Description:** Map quantum affective output to deterministic, explainable TTS suggestions (e.g. recommended speed multiplier and pitch variance).

#### FR-027: Quantum Semantic State Overlap (Kernel Fidelity)
* **Description:** Compute transition fidelity between two text prompts $A$ and $B$: $K(A, B) = |\langle \phi(A) | \phi(B) \rangle|^2$ using Qiskit Aer state inversion circuits $U^\dagger(B) U(A) |0\rangle$.

#### FR-028: Interactive Circuit Sandbox
* **Description:** Visual circuit composer supporting single-qubit gates (H, X, Y, Z, Rx, Ry, Rz) and two-qubit entanglers (CNOT, CZ, SWAP). Returns measurement probability distributions, ASCII circuit diagrams, and OpenQASM 2.0 source.

#### FR-029: Decoherence & Hardware Noise Simulation
* **Description:** Optional simulated quantum hardware noise using `qiskit_aer.noise.depolarizing_error` demonstrating environmental decoherence to users.

#### FR-030: Empirical Classical vs. Quantum Benchmarking
* **Description:** Controlled side-by-side benchmark comparing classical Logistic Regression with VQC on identical datasets. Reports Accuracy, F1-score, and wall-clock execution latency.
* **Honest Benchmark Rule:** Transparently display quantum simulation overhead without unsubstantiated claims of quantum superiority.

---

### 4.5 Category E: Security & Access Control (FR-SEC)

#### FR-031: Secret Key Isolation
* **Description:** Sensitive credentials (`ELEVENLABS_API_KEY`, `SECRET_KEY`, `DATABASE_URL`) must exist exclusively in server-side environment variables and never be emitted in client bundles or public API responses.

#### FR-032: Password Hashing & Salt
* **Description:** Passwords stored using bcrypt with cryptographic salt; plain-text passwords must never be logged or stored.

#### FR-033: Cross-Origin Resource Sharing (CORS)
* **Description:** FastAPI CORS middleware strictly configured to allow requests only from authorized frontend origins (e.g., `http://localhost:3000` in development, Vercel production domain in production).

#### FR-034: Rate Limiting & Abuse Prevention
* **Description:** Enforce request rate limiting on synthesis and quantum endpoints to prevent resource exhaustion.

---

## 5. Non-Functional Requirements (NFR)

| ID | Category | Specification |
| :--- | :--- | :--- |
| **NFR-001** | **Security** | Zero credential leaks. Passwords salted with bcrypt. HTTPS-only communication in production. Bearer JWT validation on all private endpoints. |
| **NFR-002** | **Reliability** | Decoupled architecture: ElevenLabs outages or quantum simulation timeouts must return graceful error envelopes and never crash the backend worker process. |
| **NFR-003** | **Maintainability** | Clean separation of concerns across presentation (React components), API routing, service layer, data repositories, database models, and provider adapters. |
| **NFR-004** | **Usability** | The core TTS workflow must be immediately usable by a non-technical individual in under 15 seconds from landing. |
| **NFR-005** | **Responsiveness** | Responsive UI adhering to mobile-first standards supporting Viewport widths from 320px (mobile) up to 2560px (ultra-wide desktop). |
| **NFR-006** | **Performance** | Audio generation response latency dominated solely by ElevenLabs provider API. Local audio streaming uses chunked partial range streaming. Database queries indexed by `user_id` and `created_at`. |
| **NFR-007** | **Deployment** | Compatible with standard cloud PaaS: Backend on Render Web Service, Database on Render PostgreSQL, Frontend on Vercel Static Hosting. |
| **NFR-008** | **Testability** | Independent automated test suites for backend unit, API, integration, and quantum modules (Pytest) and frontend component/store logic (Vitest). |
| **NFR-009** | **Extensibility** | Dynamic registration of new voice providers, additional language locales, or new quantum ansatz circuits without architectural rewrite. |
| **NFR-010** | **Observability** | Structured console application logging with timestamped request tracing and `/api/v1/health` heartbeat. |

---

## 6. Quantum Requirements (QR)

| ID | Title | Specification |
| :--- | :--- | :--- |
| **QR-001** | Decoupled Execution | Quantum module failures must never block or prevent core speech synthesis. |
| **QR-002** | Simulation Feasibility | All quantum circuits must execute on local classical simulators (Qiskit Aer and PennyLane `default.qubit`) within a reasonable bound (qubit count $\le 8$, shots $\le 1024$). |
| **QR-003** | Feature Normalization | Feature vectors mapped strictly to $[0, \pi]$ using MinMax scaling to prevent angle phase wrapping anomalies. |
| **QR-004** | Deterministic Seed Support | Benchmarks and circuit simulations must support reproducible execution seeds. |
| **QR-005** | Entanglement Representation | Circuit architectures must include controlled two-qubit operations (CNOT/CZ) to generate verifiable non-zero quantum state entanglement. |
| **QR-006** | Honest Benchmarking | Reporting of classical vs. quantum results must include latency, showing the simulation overhead of quantum algorithms on classical hardware without exaggerated claims. |

---

## 7. Deployment Requirements (DR)

| ID | Title | Specification |
| :--- | :--- | :--- |
| **DR-001** | Backend PaaS | FastAPI backend deployable on Render via standard Docker or Python Web Service blueprint. |
| **DR-002** | Managed PostgreSQL | PostgreSQL 16+ on Render connected via encrypted `DATABASE_URL` with automatic Alembic migrations on startup. |
| **DR-003** | Frontend Edge Hosting | React Vite SPA deployed on Vercel with single-page routing rewrite configuration (`vercel.json`). |
| **DR-004** | Cross-Origin Communication | Configured CORS headers on FastAPI matching the Vercel production deployment URL. |
| **DR-005** | Environment Configuration | Complete `.env.example` defining all required configuration keys without sensitive defaults. |
| **DR-006** | Health Heartbeat | Public `GET /api/v1/health` endpoint responding with HTTP 200 for Render zero-downtime health probes. |

---

## 8. Standard Error Catalog & Behavior Contract

All API errors adhere to this deterministic JSON structure:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable safe explanation.",
    "details": null
  }
}
```

| HTTP Status | Error Code | Trigger Condition | System Reaction |
| :--- | :--- | :--- | :--- |
| **400 / 422** | `EMPTY_TEXT` | Text is empty, null, or whitespace only. | Block provider call; return friendly validation error. |
| **400 / 422** | `TEXT_TOO_LONG` | Text exceeds 2,500 characters. | Block provider call; specify excess character count. |
| **400 / 422** | `INVALID_LANGUAGE` | Language code not supported. | Reject request; return supported language list. |
| **400 / 422** | `INVALID_VOICE` | Voice ID not found in active registry. | Reject request; suggest valid active voices. |
| **400 / 422** | `VOICE_LANGUAGE_MISMATCH` | Voice incompatible with selected language. | Reject request; instruct user to select matching voice. |
| **401** | `UNAUTHORIZED` | Missing, invalid, or expired JWT. | Challenge request; redirect user to login. |
| **403** | `FORBIDDEN` | Accessing another user's generation or favorite. | Deny access immediately; log security event. |
| **502** | `PROVIDER_ERROR` | ElevenLabs returns error (e.g. quota, bad key). | Map raw provider error to safe generic message; offer retry. |
| **504** | `PROVIDER_TIMEOUT` | ElevenLabs takes $> 15\text{s}$ to respond. | Cancel request; return timeout error to client. |
| **429** | `PROVIDER_RATE_LIMIT` | ElevenLabs or backend rate limit hit. | Inform user of temporary limit; include retry-after header. |
| **500** | `DATABASE_ERROR` | Database connection failure or query crash. | Log exception server-side; return safe service unavailable notice. |
| **500** | `QUANTUM_EXECUTION_ERROR` | Qiskit / PennyLane simulator exception. | Return failure within quantum envelope; leave TTS unaffected. |
| **500** | `INTERNAL_SERVER_ERROR` | Unhandled backend exception. | Mask stack trace; log traceback; return generic safe message. |
