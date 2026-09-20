# Bloop — Product Scope & Boundary Contract

**Document Identifier:** BLOOP-SCOPE-V1  
**Project:** Bloop — AI Text-to-Speech & Quantum Intelligence Platform  
**Target Milestone:** Intermediate-Level MVP  
**Status:** Approved Scope Definition  
**Authority:** Bloop Master Prompt & Prompt 01

---

## 1. System Scope Overview

Bloop is strictly positioned as an **Intermediate-Level Full-Stack AI Application**. It bridges commercial-grade speech synthesis via ElevenLabs with an educational, research-oriented Quantum Intelligence laboratory.

The project purposefully rejects two extremes:
1. **The "Toy MVP"**: A trivial script or unauthenticated single-page prototype with hardcoded mocks and zero persistence.
2. **The "Over-Engineered Enterprise Platform"**: A distributed multi-tenant microservices architecture with Kafka, Kubernetes, billing systems, and enterprise organizations.

Bloop is engineered for **depth, architectural correctness, security, and educational elegance**.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             BLOOP SYSTEM BOUNDARY                           │
│                                                                             │
│  ┌─────────────────────────┐           ┌─────────────────────────────────┐  │
│  │   Core TTS Subsystem    │           │  Quantum Intelligence Subsystem │  │
│  │                         │           │                                 │  │
│  │  • Text Input & Limits  │           │  • Angle Encoding (Hilbert)     │  │
│  │  • ISO Languages        │           │  • Variational Classifier (VQC) │  │
│  │  • Dynamic Voice Registry│   STRICT  │  • Emotion QNN (PennyLane)      │  │
│  │  • ElevenLabs Adapter   │ DECOUPLING│  • State Overlap Fidelity       │  │
│  │  • Streamed Playback    │◄─────────►│  • Circuit Sandbox & Noise      │  │
│  │  • Audio Download       │           │  • Classical vs Quantum Bench   │  │
│  └────────────┬────────────┘           └────────────────┬────────────────┘  │
│               │                                         │                   │
│               └───────────────────┬─────────────────────┘                   │
│                                   ▼                                         │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                 User Platform & Data Persistence Layer                │  │
│  │                                                                       │  │
│  │  • User Registration & Bcrypt Authentication                          │  │
│  │  • JWT Session Management                                             │  │
│  │  • Speech Generation History (Metadata Only)                          │  │
│  │  • Bookmarked Favorites                                               │  │
│  │  • Multi-Parametric Search, Filtering, Sorting & Pagination           │  │
│  │  • Strict Per-User Data Isolation                                     │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. In-Scope Components (Intermediate-Level Contract)

The following components and subsystems are fully in-scope for the Bloop Intermediate-Level implementation:

### 2.1 Core Speech Platform
* Real-time text analysis: live character count, word count, estimated speech duration.
* Validation guards: empty text rejection and maximum text limit enforcement (2,500 characters).
* Dynamic ISO language registry (`en-US`, `en-GB`, `es-ES`, `fr-FR`, `de-DE`, `hi-IN`).
* Extensible dynamic voice registry decoupled from proprietary vendor identifiers.
* ElevenLabs synthesis integration mediated strictly through the FastAPI backend.
* Offline simulation audio provider fallback when `ELEVENLABS_API_KEY` is not present.
* Interactive audio player with play/pause, seek scrubber, volume control, and playback rate adjustment.
* Audio download endpoint delivering standard MP3 attachments.

### 2.2 Backend & Data Persistence
* FastAPI REST application with strict `/api/v1` route versioning.
* Uniform JSON envelope contract for all success and error responses.
* Pydantic v2 input validation with descriptive error details.
* SQLAlchemy 2.0 ORM models with Alembic schema migration management.
* PostgreSQL database support (production on Render) with SQLite development fallback.
* Isolated per-user storage for speech history, bookmarked favorites, and user preferences.
* Audio file persistence on server storage with HTTP `Range` streaming support.

### 2.3 User Security & Authentication
* Registration and login endpoints with bcrypt password hashing and cryptographic salt.
* Bearer JWT token issuance, verification, and revocation on logout.
* Protected API routes enforcing token authorization.
* Strict tenant isolation: User A cannot read, query, or delete User B's records.
* CORS headers locking API access to trusted frontend client origins.

### 2.4 Quantum Intelligence Subsystem
* Classical-to-quantum angle feature mapping into qubit Hilbert statevectors.
* Variational Quantum Classifier (VQC) with parameterized rotation and entangling ansatz layers.
* PennyLane hybrid quantum neural network evaluating 4 affective wires and state entanglement entropy.
* Quantum semantic state overlap computation via inversion circuits on Qiskit Aer.
* Interactive circuit sandbox supporting single-qubit and two-qubit gates with OpenQASM export.
* Simulated environmental decoherence using depolarizing error noise models.
* Empirical benchmark comparing classical Logistic Regression vs VQC across accuracy and latency.

### 2.5 Cloud Deployment Architecture
* Render Web Service running FastAPI via Uvicorn.
* Managed Render PostgreSQL database with automated migration execution on deploy.
* Vercel static hosting running the React + Vite single-page application.
* Automated health check endpoint (`/api/v1/health`) for PaaS uptime monitoring.

---

## 3. The Voice Scope Rule (Section 24)

The voice architecture is a foundational design requirement, but **hardcoding a static voice catalogue is strictly prohibited**.

### What MUST Be Built:
1. **Voice Domain Model:** Entity schema defining `voice_id`, `name`, `language_code`, `gender`, `accent`, `provider`, and `is_active`.
2. **Dynamic Retrieval Architecture:** API routes (`GET /api/v1/voices`) and frontend selectors that query available voices dynamically from backend state.
3. **Provider Abstraction:** An adapter layer separating internal voice entities from vendor-specific API formats.
4. **Validation Mechanism:** Strict verification that a requested `voice_id` exists in the active registry and is compatible with the selected `language_code`.
5. **Runtime Injection Points:** Interfaces allowing developers and users to add actual ElevenLabs voice IDs without code modifications:
   * Direct UI Modal ("Inject Custom Voice ID").
   * External configuration file (`backend/voices_config.json`) with reload endpoint.
   * REST endpoint (`POST /api/v1/voices`).
6. **Simulation Fallback:** A local synthetic audio generator allowing full end-to-end testing when no ElevenLabs API key is configured.

### What Must NOT Be Built:
1. **Zero Invented Voice IDs:** Do not make up fake IDs like `eleven_voice_123` or pretend arbitrary strings exist on ElevenLabs.
2. **Zero Fake Voice Names:** Do not pretend fictional character voices belong to ElevenLabs.
3. **Zero Hardcoded Catalogues:** Do not bake a static dictionary of proprietary ElevenLabs voices into the frontend or backend application code.

---

## 4. The Language Scope Rule (Section 25)

Supported languages must be managed as dynamic, authoritative domain entities:

```
Language (ISO Code) ──► Provider Capability ──► Compatible Voices ──► Frontend Selector
```

### Architectural Principles:
* **No Scattered String Literals:** Language codes (`en-US`, `es-ES`, etc.) must not be hardcoded across disparate components or routes.
* **Backend Authority:** The backend database / configuration is the single source of truth for active languages (`GET /api/v1/languages`).
* **Extensibility:** Introducing a new language locale must only require adding an entry in the backend repository or database without modifying UI business logic.

---

## 5. The Quantum Scope Boundary (Section 33)

The Quantum Intelligence layer is an **educational and scientific experimentation laboratory**.

### Boundaries & Constraints:
* **Strict Decoupling Invariant:** The core TTS platform must never have a runtime dependency on quantum modules. If Qiskit or PennyLane crash, fail, or run out of memory, TTS continues with 100% availability.
* **Simulator Based:** All quantum execution runs on classical simulator engines (`Qiskit Aer` and PennyLane `default.qubit`). Physical QPU access (e.g. IBM Quantum Experience cloud tokens) is outside the MVP boundary.
* **Bounded Resource Utilization:** Circuit depth and qubit counts must remain computationally lightweight ($\le 8$ qubits, $\le 1024$ shots) to execute within typical HTTP request timeouts ($< 5\text{s}$).
* **Honest Benchmarking Mandate:** Quantum algorithms must never be marketed as having immediate "quantum supremacy" or intrinsic superiority. Results must empirically report wall-clock simulation overhead and classical baseline comparisons.

---

## 6. Data Ownership & Privacy Boundary (Section 26)

User-owned data must remain strictly isolated:

```
┌────────────────────────┐         ┌────────────────────────┐
│         User A         │         │         User B         │
├────────────────────────┤         ├────────────────────────┤
│ • History Items (A)    │         │ • History Items (B)    │
│ • Audio Files (A)      │         │ • Audio Files (B)      │
│ • Bookmarks / Favs (A) │         │ • Bookmarks / Favs (B) │
│ • Preferences (A)      │         │ • Preferences (B)      │
└────────────────────────┘         └────────────────────────┘
          ▲                                   ▲
          │                                   │
      ISOLATED                            ISOLATED
   Database Tenant                     Database Tenant
```

* Every private record must contain a foreign key `user_id`.
* The data access layer (repositories) must automatically inject `WHERE user_id = :current_user_id` into all queries.
* Audio filenames must be hashed with non-guessable UUIDs to prevent enumeration.

---

## 7. Explicitly Out-of-Scope Features (Section 23)

To maintain top-tier intermediate-level quality and prevent unnecessary bloat, the following enterprise and complex distributed features are **explicitly excluded** from the MVP:

| Excluded Feature | Architectural Rationale for Exclusion |
| :--- | :--- |
| **Payment & Billing Systems (Stripe/PayPal)** | Bloop is a portfolio/educational application; subscription billing introduces regulatory and PCI compliance overhead. |
| **Enterprise Organizations & Team Workspaces** | Multi-tenant RBAC, role inheritance, and team invites dilute the core TTS and Quantum product focus. |
| **Kubernetes / Helm / Service Mesh** | Render PaaS and Vercel edge hosting provide reliable hosting without infrastructure complexity. |
| **Distributed Message Brokers (Kafka / RabbitMQ)** | Asynchronous event streaming is unnecessary for synchronous TTS and fast local quantum simulations. |
| **Distributed Cache Clusters (Redis / Memcached)** | Local in-memory caching and database indexing are sufficient for intermediate traffic loads. |
| **Commercial Voice Marketplace** | Buying, selling, or training custom voices requires complex licensing and large-scale cloud storage. |
| **Multi-Cloud Object Storage (AWS S3 / GCP Storage)** | Server-side directory storage is simpler, faster to test locally, and fully supported on Render persistent disks. |
| **Native Mobile Applications (iOS / Android)** | Responsive web frontend provides high-quality mobile browser access without maintaining multiple codebases. |
| **Conversational AI Chatbots & Autonomous Agents** | Bloop is a Text-to-Speech synthesis platform, not an LLM chat assistant. |
| **Physical QPU Hardware Cloud Connection** | Cloud QPUs introduce long queue delays (minutes to hours) unsuitable for interactive web UI interactions. |

---

## 8. Scope Control & Change Management Procedure (Sections 44 & 45)

1. **The Scope Freeze Rule:** No new features may be introduced during subsequent prompts unless they are explicitly authorized by the Bloop Master Prompt.
2. **Future Enhancements Protocol:** If an architectural optimization or new feature is identified, it must be documented in `docs/feature-matrix.md` under `FUTURE` rather than silently added to the codebase.
3. **Conflict Resolution:** If a later prompt conflicts with this Scope Contract, the higher-level principles of the Master Prompt take precedence, and the architectural decision must be logged in the project architecture documentation.
