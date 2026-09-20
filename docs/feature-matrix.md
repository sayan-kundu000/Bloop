# Bloop — Feature Classification & End-to-End Traceability Matrix

**Document Identifier:** BLOOP-MATRIX-V1  
**Project:** Bloop — AI Text-to-Speech & Quantum Intelligence Platform  
**Target Milestone:** Intermediate-Level MVP  
**Status:** Approved Product-Scope Contract  
**Authority:** Bloop Master Prompt & Prompt 01

---

## 1. Feature Classification Taxonomy

Every capability, module, and feature in Bloop belongs to **exactly one** of the following five classification categories:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       BLOOP 5-TIER CLASSIFICATION                           │
├────────────────────┬────────────────────────────────────────────────────────┤
│ 1. CORE            │ Fundamental speech synthesis & user interaction engine │
│ 2. INTERMEDIATE MVP│ Multi-user persistence, quantum laboratory & cloud ops │
│ 3. SUPPORTING      │ Developer ergonomics, simulation fallback, docs & tests│
│ 4. FUTURE          │ Planned enhancements deferred to post-MVP milestones  │
│ 5. OUT OF SCOPE    │ Explicitly forbidden enterprise bloat & architecture   │
└────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 2. Feature Classification Table

| Feature Name | Category | Rationale & Architectural Scope |
| :--- | :--- | :--- |
| **Text Input & Live Metrics** | `CORE` | Primary user input mechanism; live character/word counters and limit alerts. |
| **Empty & Boundary Validation** | `CORE` | Defensive guard preventing wasteful provider API calls or payload overflows. |
| **Language Selection** | `CORE` | ISO language selection (`en-US`, `es-ES`, etc.) driving dynamic voice filters. |
| **Dynamic Voice Architecture** | `CORE` | Decoupled voice registry with runtime voice injection and zero hardcoded IDs. |
| **ElevenLabs Synthesis Adapter** | `CORE` | Server-side integration mediating speech synthesis via ElevenLabs API. |
| **Interactive Audio Player** | `CORE` | Audio playback with play/pause, scrub bar, volume slider, and playback rate. |
| **Audio File Download** | `CORE` | Direct client download of synthesized MP3 files. |
| **User Registration & Login** | `INTERMEDIATE MVP` | Secure user authentication with bcrypt password hashing and JWT sessions. |
| **Protected API Routes** | `INTERMEDIATE MVP` | Bearer token authorization securing user data endpoints. |
| **User Preferences** | `INTERMEDIATE MVP` | Persistent storage of user UI theme, default language, and default playback speed. |
| **Speech Generation History** | `INTERMEDIATE MVP` | Persistent PostgreSQL records of all user speech generations with metadata. |
| **Favorites / Bookmarking** | `INTERMEDIATE MVP` | User bookmarks linking to speech generations with dedicated view. |
| **Multi-Parametric Search & Filter** | `INTERMEDIATE MVP` | Substring text search, language filtering, voice filtering, and sorting. |
| **History Pagination** | `INTERMEDIATE MVP` | Server-side pagination handling large history datasets efficiently. |
| **Per-User Tenant Isolation** | `INTERMEDIATE MVP` | Enforces that users can only access their own private data and audio files. |
| **Quantum Text VQC Classifier** | `INTERMEDIATE MVP` | Qiskit Aer Hilbert space angle encoding and Variational Quantum Classification. |
| **Quantum Emotion QNN (PennyLane)**| `INTERMEDIATE MVP` | Hybrid QNN evaluating affective wires and state entanglement entropy. |
| **Quantum Semantic State Overlap** | `INTERMEDIATE MVP` | State inversion transition fidelity $|⟨\phi(A)|\psi(B)⟩|^2$ on Qiskit Aer. |
| **Interactive Circuit Sandbox** | `INTERMEDIATE MVP` | Visual quantum circuit composer with single/two-qubit gates and OpenQASM export. |
| **Hardware Noise Simulation** | `INTERMEDIATE MVP` | Depolarizing error noise models simulating environmental decoherence. |
| **Classical vs Quantum Benchmark** | `INTERMEDIATE MVP` | Empirical comparison of Logistic Regression vs VQC across accuracy and latency. |
| **Cloud Deployment (Render/Vercel)**| `INTERMEDIATE MVP` | Full production deployment: FastAPI + PostgreSQL on Render, React on Vercel. |
| **Simulation TTS Provider** | `SUPPORTING` | Local synthetic audio generator for testing without an ElevenLabs API key. |
| **OpenAPI / Swagger Docs** | `SUPPORTING` | Auto-generated interactive API documentation at `/docs`. |
| **Postman Collection (v2.1)** | `SUPPORTING` | Pre-configured API test collection with automatic JWT variable handling. |
| **Database Migrations (Alembic)**| `SUPPORTING` | Version-controlled schema migrations for PostgreSQL and SQLite. |
| **Automated Test Suites** | `SUPPORTING` | Automated Pytest backend suite and Vitest frontend test suite. |
| **Health Heartbeat Endpoint** | `SUPPORTING` | Public `/api/v1/health` endpoint for cloud uptime monitoring probes. |
| **Real-Time WebSocket Streaming** | `FUTURE` | Streaming audio chunks over WebSockets as they arrive from ElevenLabs. |
| **Custom Voice Cloning UI** | `FUTURE` | In-app audio sample recording and direct instant voice cloning upload. |
| **SSML Tag Editor** | `FUTURE` | Graphical markup editor for Speech Synthesis Markup Language tags. |
| **Multi-Speaker Dialogue Studio** | `FUTURE` | Script editor assigning different voices to multiple dialogue speakers. |
| **Podcast Export Formatters** | `FUTURE` | Automated RSS feed and chapter metadata generation for generated speech. |
| **Physical QPU Hardware Execution** | `FUTURE` | Cloud queue dispatching to IBM Quantum physical superconducting QPUs. |
| **Subscription & Payment System** | `OUT OF SCOPE` | Stripe/PayPal billing, checkout funnels, and paid subscription plans. |
| **Enterprise Organizations & RBAC** | `OUT OF SCOPE` | Multi-tenant organization hierarchies, seat licensing, and team sharing. |
| **Kubernetes / Service Mesh** | `OUT OF SCOPE` | Enterprise cluster orchestration (Render PaaS satisfies all requirements). |
| **Message Brokers (Kafka/RabbitMQ)**| `OUT OF SCOPE` | Distributed asynchronous message brokers (adds unneeded operational overhead). |
| **Distributed Cache (Redis/Memcached)**| `OUT OF SCOPE` | Distributed memory caches (in-memory caching and DB indexes are sufficient). |
| **Commercial Voice Marketplace** | `OUT OF SCOPE` | Public user-to-user voice buying, selling, and revenue sharing. |
| **Native Mobile Apps (iOS/Android)** | `OUT OF SCOPE` | Dedicated native app builds (responsive mobile web SPA is fully supported). |
| **AI Conversational Chatbot** | `OUT OF SCOPE` | Conversational LLM agents or chatbots (Bloop is a focused TTS/Quantum tool). |

---

## 3. End-to-End Traceability Matrix (Section 43)

The following matrix establishes unbroken traceability from the **Source Specifications** through the **Bloop Requirement IDs**, **Feature Classification**, **Target Implementation Prompts**, and **Acceptance Criteria**:

| Source Specification | Bloop Requirement ID | Feature Name | Category | Target Prompt | Verification / Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TTS Spec §2** | `FR-001`, `BR-002` | Text Input & Live Metrics | `CORE` | Prompt 04 (Core TTS) | `AC-TTS-001`, `AC-TTS-002`, `AC-TTS-003` |
| **TTS Spec §2** | `FR-002`, `NFR-002` | Empty Text Validation | `CORE` | Prompt 04 (Core TTS) | `AC-TTS-004`, `AC-TTS-005` |
| **TTS Spec §2** | `FR-003`, `NFR-002` | Max Length Enforcement | `CORE` | Prompt 04 (Core TTS) | `AC-TTS-006`, `AC-TTS-007` |
| **TTS Spec §3** | `FR-004`, `BR-004` | Language Selection | `CORE` | Prompt 04 (Core TTS) | `AC-TTS-008` |
| **Master Prompt §24**| `FR-005`, `BR-003` | Dynamic Voice Architecture | `CORE` | Prompt 02, 04 | `AC-TTS-009`, `AC-TTS-010` |
| **TTS Spec §4** | `FR-006`, `BR-001` | ElevenLabs TTS Backend | `CORE` | Prompt 04 (Core TTS) | `AC-TTS-011`, `AC-TTS-012` |
| **TTS Spec §5** | `FR-007`, `BR-002` | Audio Player & Scrubber | `CORE` | Prompt 05 (Frontend) | `AC-TTS-013`, `AC-TTS-014`, `AC-TTS-015` |
| **TTS Spec §5** | `FR-008`, `BR-002` | Audio File Download | `CORE` | Prompt 04, 05 | `AC-TTS-016` |
| **Master Prompt §6** | `FR-015`, `BR-005` | User Registration & Bcrypt | `INTERMEDIATE MVP` | Prompt 03, 04 | `AC-USR-001` |
| **Master Prompt §6** | `FR-016`, `BR-005` | JWT Authentication | `INTERMEDIATE MVP` | Prompt 03, 04 | `AC-USR-002`, `AC-USR-003` |
| **Master Prompt §6** | `FR-017`, `BR-005` | User Profile & Preferences | `INTERMEDIATE MVP` | Prompt 03, 06 | `AC-USR-004` |
| **Master Prompt §12**| `FR-018`, `BR-006` | Speech History Persistence | `INTERMEDIATE MVP` | Prompt 03, 06 | `AC-USR-005` |
| **Master Prompt §13**| `FR-019`, `BR-006` | Favorites Bookmarking | `INTERMEDIATE MVP` | Prompt 03, 06 | `AC-USR-006` |
| **Master Prompt §14**| `FR-020`, `BR-006` | Search, Filter & Pagination| `INTERMEDIATE MVP` | Prompt 03, 06 | `AC-USR-007`, `AC-USR-008`, `AC-USR-009` |
| **Master Prompt §26**| `FR-021`, `NFR-001` | Per-User Data Isolation | `INTERMEDIATE MVP` | Prompt 03, 06 | `AC-USR-010`, `AC-USR-011` |
| **Master Prompt §15**| `FR-022`, `FR-023` | Quantum Text VQC Classifier | `INTERMEDIATE MVP` | Prompt 07 (Quantum) | `AC-QNT-001`, `AC-QNT-002` |
| **Master Prompt §16**| `FR-024`, `FR-025` | PennyLane Emotion QNN | `INTERMEDIATE MVP` | Prompt 07 (Quantum) | `AC-QNT-003`, `AC-QNT-004` |
| **Master Prompt §16**| `FR-026`, `QR-001` | Explainable Voice Tuning | `INTERMEDIATE MVP` | Prompt 07 (Quantum) | `AC-QNT-005` |
| **Master Prompt §17**| `FR-027`, `QR-005` | Quantum Semantic Overlap | `INTERMEDIATE MVP` | Prompt 07 (Quantum) | `AC-QNT-006` |
| **Master Prompt §18**| `FR-028`, `FR-029` | Circuit Lab & Noise Sim | `INTERMEDIATE MVP` | Prompt 07 (Quantum) | `AC-QNT-007`, `AC-QNT-008`, `AC-QNT-009` |
| **Master Prompt §19**| `FR-030`, `QR-006` | Honest Empirical Benchmark | `INTERMEDIATE MVP` | Prompt 07 (Quantum) | `AC-QNT-010` |
| **Master Prompt §20**| `FR-031`, `NFR-001` | Secret Protection | `INTERMEDIATE MVP` | Prompt 02, 08 | `AC-SEC-001` |
| **Master Prompt §20**| `FR-033`, `NFR-001` | CORS Configuration | `INTERMEDIATE MVP` | Prompt 02, 08 | `AC-SEC-003` |
| **Master Prompt §20**| `NFR-008`, `BR-008` | Pytest & Vitest Suites | `SUPPORTING` | Prompt 08 (Testing) | `AC-NFR-005` |
| **Master Prompt §20**| `NFR-010`, `DR-006` | Health Check Endpoint | `SUPPORTING` | Prompt 02, 09 | `AC-NFR-006`, `AC-DEP-008` |
| **Master Prompt §34**| `DR-001` to `DR-005`| Render & Vercel Deployment | `INTERMEDIATE MVP` | Prompt 09 (Deploy) | `AC-DEP-001` to `AC-DEP-007` |

---

## 4. Scope Governance & Enforcement Rules

1. **Unilateral Scope Freeze:** No engineering prompt may alter or expand any item categorized as `OUT OF SCOPE` or promote a `FUTURE` feature into the MVP without an updated Master Prompt instruction.
2. **Acceptance Gate:** Implementation prompts must demonstrate compliance with the corresponding Acceptance Criteria before code is marked complete.
3. **Traceability Verification:** Any newly added API route, database column, or frontend view must cite its governing Requirement ID (`FR-xxx`, `BR-xxx`, or `QR-xxx`).
