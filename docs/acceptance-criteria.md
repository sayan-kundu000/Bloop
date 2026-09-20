# Bloop — Acceptance Criteria & Verification Framework

**Document Identifier:** BLOOP-AC-V1  
**Project:** Bloop — AI Text-to-Speech & Quantum Intelligence Platform  
**Target Milestone:** Intermediate-Level MVP  
**Status:** Approved Acceptance Standard  
**Authority:** Bloop Master Prompt & Prompt 01

---

## 1. Overview & Verification Standards

This document establishes the binding acceptance criteria for the Bloop Intermediate-Level MVP. Each criterion defines a measurable, testable condition that must be verified through automated testing or deterministic manual procedures before a feature is considered complete.

---

## 2. Category A: Core Text-to-Speech Acceptance Criteria (AC-TTS)

| Criterion ID | Target Requirement | Acceptance Condition | Verification Method |
| :--- | :--- | :--- | :--- |
| **AC-TTS-001** | `FR-001` | User can input text into the workspace textarea via typing or clipboard paste. | Automated UI / Manual |
| **AC-TTS-002** | `FR-001` | Character count accurately reflects the current length in real time as characters are typed or deleted. | Unit Test / Vitest |
| **AC-TTS-003** | `FR-001` | Word count accurately reflects whitespace-delimited tokens in real time. | Unit Test / Vitest |
| **AC-TTS-004** | `FR-002` | Submitting empty or whitespace-only text is rejected by the frontend without triggering an API call. | Component Test |
| **AC-TTS-005** | `FR-002` | Direct API request with empty or whitespace-only text returns HTTP 422 with code `EMPTY_TEXT` and zero provider calls. | Backend Pytest |
| **AC-TTS-006** | `FR-003` | Pasting or typing $> 2,500$ characters disables the generate button and displays a crimson boundary warning. | Component Test |
| **AC-TTS-007** | `FR-003` | Backend independently validates text length and rejects requests $> 2,500$ characters with HTTP 422 `TEXT_TOO_LONG`. | Backend Pytest |
| **AC-TTS-008** | `FR-004` | Language selector allows choosing from supported ISO locales (`en-US`, `en-GB`, `es-ES`, `fr-FR`, `de-DE`, `hi-IN`). | Integration Test |
| **AC-TTS-009** | `FR-005` | Voice architecture retrieves voices dynamically from the backend without hardcoded static lists in the frontend. | API & UI Test |
| **AC-TTS-010** | `FR-005` | User can inject custom ElevenLabs voice IDs via modal, config file, or REST API without altering application source code. | Integration Test |
| **AC-TTS-011** | `FR-006` | Backend attaches server-side `ELEVENLABS_API_KEY` and synthesizes audio. The client bundle contains zero API keys. | Security Audit |
| **AC-TTS-012** | `FR-006` | When `ELEVENLABS_API_KEY` is missing, the backend automatically falls back to an offline simulation provider with zero crashes. | Backend Pytest |
| **AC-TTS-013** | `FR-007` | Synthesized audio stream loads into the interactive player and responds to Play and Pause commands. | Vitest / Manual |
| **AC-TTS-014** | `FR-007` | Seeking on the scrubber bar requests byte ranges via HTTP `Range` headers and streams smoothly. | Network Inspection |
| **AC-TTS-015** | `FR-007` | Volume slider adjusts audio gain, mute button toggles state, and playback speed adjusts pitch/rate correctly. | Component Test |
| **AC-TTS-016** | `FR-008` | Clicking "Download" triggers immediate download of an `.mp3` audio file with valid ID3/MPEG headers. | Browser & API Test |
| **AC-TTS-017** | `FR-009` | Errors from provider timeouts or rate limits display human-readable toasts with a retry button. | E2E Scenario Test |

---

## 3. Category B: User Platform & Persistence Criteria (AC-USR)

| Criterion ID | Target Requirement | Acceptance Condition | Verification Method |
| :--- | :--- | :--- | :--- |
| **AC-USR-001** | `FR-015` | User registration validates email format and password length ($\ge 8$ chars) and stores salted bcrypt hashes in PostgreSQL. | Backend Pytest |
| **AC-USR-002** | `FR-016` | User login verifies credentials and returns a valid signed JWT containing user ID and expiration timestamp. | Backend Pytest |
| **AC-USR-003** | `FR-016` | Unauthenticated requests to protected endpoints return HTTP 401 `UNAUTHORIZED`. | Backend Pytest |
| **AC-USR-004** | `FR-017` | Authenticated users can retrieve and update preferences (theme, default voice, default speed) with persistent storage. | API & UI Test |
| **AC-USR-005** | `FR-018` | Every successful speech generation creates a persistent database record linked to `user_id` with metadata. | Database Test |
| **AC-USR-006** | `FR-019` | User can bookmark and unbookmark any generation; bookmarked items appear in the `/favorites` view. | Integration Test |
| **AC-USR-007** | `FR-020` | History view supports text search matching substrings within the generated text. | Repository Test |
| **AC-USR-008** | `FR-020` | History view filters by language locale and voice ID accurately. | Repository Test |
| **AC-USR-009** | `FR-020` | History pagination returns accurate `total`, `page`, `page_size`, and `has_next` metadata. | API Test |
| **AC-USR-010** | `FR-021` | User A cannot view, retrieve, or delete records belonging to User B (tenant isolation). | Security Test |
| **AC-USR-011** | `FR-021` | Attempting to access an audio file or history record belonging to another user returns HTTP 403 or 404. | Security Test |

---

## 4. Category C: Quantum Intelligence Platform Criteria (AC-QNT)

| Criterion ID | Target Requirement | Acceptance Condition | Verification Method |
| :--- | :--- | :--- | :--- |
| **AC-QNT-001** | `FR-022`, `QR-003` | Feature extraction maps text attributes to $[0, \pi]$ rotation angles without phase wrapping anomalies. | Quantum Unit Test |
| **AC-QNT-002** | `FR-023` | Variational Quantum Classifier (VQC) executes on Qiskit Aer (`AerSimulator`) and returns valid style probabilities summing to 1.0. | Pytest (Qiskit) |
| **AC-QNT-003** | `FR-024` | PennyLane Hybrid QNN executes across 4 affective wires using `default.qubit` device. | Pytest (PennyLane) |
| **AC-QNT-004** | `FR-025` | State Shannon entanglement entropy $H = -\sum p_i \log_2(p_i)$ is computed and returns a non-negative scalar. | Math Validation Test |
| **AC-QNT-005** | `FR-026` | Emotion output produces explainable, bounded speech parameter recommendations (speed, pitch). | Unit Test |
| **AC-QNT-006** | `FR-027` | Semantic similarity kernel executes state inversion circuit $U^\dagger(B) U(A) |0\rangle$ and returns fidelity $\in [0, 1]$. | Pytest (Qiskit) |
| **AC-QNT-007** | `FR-028` | Circuit sandbox accepts arbitrary gate compositions (H, X, Y, Z, Rx, Ry, Rz, CNOT, CZ, SWAP) and returns probability distributions. | Sandbox API Test |
| **AC-QNT-008** | `FR-028` | Circuit sandbox generates valid ASCII circuit wire diagrams and exportable OpenQASM 2.0 source code. | Parser Test |
| **AC-QNT-009** | `FR-029` | Depolarizing noise model simulation introduces measurable dispersion into ideal measurement distributions. | Noise Test |
| **AC-QNT-010** | `FR-030`, `QR-006` | Controlled benchmark runs classical Logistic Regression and VQC on identical data, reporting Accuracy, F1, and execution latency without supremacy claims. | Benchmark Test |
| **AC-QNT-011** | `QR-001` | A simulated failure or timeout in any quantum module returns an error envelope without degrading core speech synthesis. | Resilience Test |

---

## 5. Category D: Security & Non-Functional Criteria (AC-SEC & AC-NFR)

| Criterion ID | Target Requirement | Acceptance Condition | Verification Method |
| :--- | :--- | :--- | :--- |
| **AC-SEC-001** | `FR-031`, `NFR-001` | Secret keys (`ELEVENLABS_API_KEY`, `SECRET_KEY`) are never present in client bundles or public API responses. | Bundle Inspection |
| **AC-SEC-002** | `FR-032` | Plain-text passwords are never stored in the database or written to log files. | Database & Log Audit |
| **AC-SEC-003** | `FR-033` | CORS middleware rejects unauthorized origins and permits configured frontend domains. | Security Test |
| **AC-NFR-001** | `NFR-002` | External provider failures return safe HTTP 502 error envelopes without crashing the backend process. | Fault Injection Test |
| **AC-NFR-002** | `NFR-004` | New users can navigate from landing to audio playback in under 15 seconds. | Usability Audit |
| **AC-NFR-003** | `NFR-005` | Frontend interface displays cleanly and functions across mobile (375px), tablet (768px), and desktop (1440px). | Responsive Testing |
| **AC-NFR-004** | `NFR-006` | Audio streaming utilizes chunked transfer encoding and partial range delivery for sub-second playback startup. | Network Audit |
| **AC-NFR-005** | `NFR-008` | Pytest backend test suite and Vitest frontend test suite execute and pass in CI/CD pipeline. | Automated CI Test |
| **AC-NFR-006** | `NFR-010` | `GET /api/v1/health` returns HTTP 200 with service, database, and provider statuses. | Smoke Test |

---

## 6. Category E: Cloud Deployment Acceptance Criteria (AC-DEP)

| Criterion ID | Target Requirement | Acceptance Condition | Verification Method |
| :--- | :--- | :--- | :--- |
| **AC-DEP-001** | `DR-001` | FastAPI backend deploys and runs on Render Web Service using Python 3.12+ and Uvicorn. | Cloud Deployment |
| **AC-DEP-002** | `DR-002` | Backend connects successfully to Render managed PostgreSQL database. | Startup Log Check |
| **AC-DEP-003** | `DR-002` | Alembic migrations execute automatically on Render deployment startup. | Migration Log Check |
| **AC-DEP-004** | `DR-003` | React frontend builds and deploys to Vercel without TypeScript or build errors. | Vercel Build Check |
| **AC-DEP-005** | `DR-003` | Vercel rewrite configuration handles direct deep linking to `/workspace`, `/history`, `/quantum` without 404s. | Browser Navigation |
| **AC-DEP-006** | `DR-004` | Frontend in Vercel communicates with Render backend over HTTPS without CORS errors. | Live Network Test |
| **AC-DEP-007** | `DR-005` | Environment variables in Render and Vercel are correctly mapped and segregated. | Environment Audit |
| **AC-DEP-008** | `DR-006` | Render health check probe detects `/api/v1/health` as healthy and maintains zero-downtime restarts. | PaaS Dashboard Check |

---

## 7. Definition of Done (DoD) for Intermediate-Level MVP

A feature or user story within Bloop is officially **Done** only when:
1. **Code Complete:** Implemented in accordance with the Product Requirements Specification and Clean Architecture layers.
2. **Type-Safe:** Zero TypeScript compilation errors in frontend (`tsc --noEmit`) and strict Pydantic v2 validation in backend.
3. **Automated Tests:** Covered by corresponding unit and integration tests passing in Pytest or Vitest.
4. **Decoupling Verified:** Quantum modules do not create dependencies in the TTS pipeline.
5. **No Secret Leaks:** Zero hardcoded API keys or secrets in source code or Git history.
6. **Error Handled:** All edge cases and error states return structured error envelopes matching the Bloop Error Catalog.
7. **Documented:** OpenAPI schema updated and documented in project references.
