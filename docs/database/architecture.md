# Bloop PostgreSQL Database Architecture

**Document Identifier:** BLOOP-DB-ARCH-007  
**Status:** Approved Technical Architecture  
**Authority:** Prompt 07 — PostgreSQL Database Architecture, SQLAlchemy 2.x Models & Alembic Migrations  
**Target Engine:** Managed PostgreSQL 16 (Render Cloud) with local SQLite fallback for isolated tests  

---

## 1. Executive Summary

Bloop utilizes a single, high-performance, normalized **PostgreSQL 16** relational database. The persistence layer is engineered with **SQLAlchemy 2.x** declarative models (`Mapped`, `mapped_column`, `relationship`, `select()`) and governed by **Alembic** schema migrations.

### Core Architectural Invariants:
1. **Zero Audio Binaries in Database:** Large audio waveforms and generated MP3 files are **NEVER** stored as database blobs. PostgreSQL exclusively persists metadata, references, formats, duration metrics, and ownership keys.
2. **PostgreSQL as Canonical Production Database:** SQLite is exclusively permitted as an offline developer fallback and isolated automated testing fixture. Production strictly requires Render Managed PostgreSQL 16.
3. **Decoupled Quantum Subsystem:** Quantum experiment persistence is strictly additive and completely decoupled from core Speech synthesis. A failure in Quantum computation or storage can never corrupt or block Text-to-Speech generation.
4. **Zero Pre-seeded Actual Voices:** In strict adherence to platform specifications, no actual ElevenLabs voice records, fake voice IDs, or hardcoded voice names are seeded into production tables. The database provides a dynamic voice registry that is populated at runtime by the user.

---

## 2. Domain Decomposition

The relational schema is decomposed into four discrete, cohesive domain areas:

```
PostgreSQL Database (bloop_db)
│
├── 1. Identity & Access Domain
│   ├── users (Authentication, credentials, lifecycle)
│   └── user_preferences (Default language/voice, theme, audio playback speed)
│
├── 2. Catalog & Dynamic Voice Domain
│   ├── languages (ISO-639 / BCP-47 locale standards)
│   └── voices (Dynamic voice registry; provider references; metadata)
│
├── 3. Speech Synthesis Domain
│   ├── speech_generations (Requests, text stats, audio references, status lifecycle)
│   └── favorites (Bookmarked user generations with unique constraints)
│
└── 4. Quantum Intelligence Domain
    └── quantum_experiments (Qiskit/PennyLane circuit logs, payloads, results JSON)
```

---

## 3. End-to-End Data Flow Architecture

The following Mermaid diagram details the execution flow from client requests through services and repositories to persistence:

```mermaid
flowchart TD
    Client["React 19 SPA (Vercel)"] -->|REST / HTTPS| Router["FastAPI Router Layer"]
    Router -->|Dependency Injection| Service["Domain Service Layer\n(TTS / Auth / Quantum)"]
    Service -->|get_db Dependency| Session["SQLAlchemy SessionLocal\n(Request-Scoped)"]
    Service -->|Business Entities| Repo["Repository Layer\n(User, Speech, Favorite, Quantum)"]
    Repo -->|SQLAlchemy 2.x select()| Engine["SQLAlchemy Engine + Pool\n(pool_size=10, max_overflow=20)"]
    Engine -->|TCP / TLS 1.3| Postgres[("Render PostgreSQL 16")]

    Service -.->|Vendor xi-api-key| ElevenLabs["ElevenLabs Cloud API\n(Outbound HTTPS)"]
    Service -.->|Local Simulation| Qiskit["Qiskit Aer / PennyLane\n(In-Memory Simulation)"]
```

---

## 4. Audio Storage & Metadata Segregation

Audio synthesis creates temporary or cached MP3 binaries. Storing these binaries directly in PostgreSQL rows causes severe page bloat, degrades buffer pool cache hit ratios, and complicates backups.

Bloop enforces a clear segregation:
- **Relational Storage:** File paths (`audio_filename`), duration (`duration_seconds`), byte size (`file_size_bytes`), format (`mp3`), external provider references (`provider_request_id`), and lifecycle status (`pending`, `processing`, `completed`, `failed`).
- **Filesystem Storage:** The actual encoded audio file is written to `AUDIO_STORAGE_PATH` (e.g. `backend/app/storage/audio/`).
- **Client Access:** Audio streaming endpoints (`/api/v1/tts/audio/{filename}`) read from disk via `FileResponse` with HTTP byte-range support.

---

## 5. Connection Pooling & Resource Governance

Render Managed PostgreSQL connections are managed via SQLAlchemy connection pooling:
- **Pool Size:** `10` persistent connections per web container.
- **Max Overflow:** `20` burst connections during traffic spikes.
- **Pre-Ping (`pool_pre_ping=True`):** Tests connection liveness with `SELECT 1` before checkout, preventing stale socket errors following network restarts.
- **Recycle Timeout (`pool_recycle=300`):** Recycles idle connections every 5 minutes to gracefully handle cloud firewall timeouts.

---

## 6. End-to-End Database Traceability Matrix

| Platform Requirement | Relational Entity | SQLAlchemy Model | Repository Layer | Primary API Route | Automated Tests |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **User Accounts & Auth** | `users` | `User` (`models/user.py`) | `UserRepository` (`repositories/user.py`) | `POST /api/v1/auth/register`<br>`POST /api/v1/auth/login` | `test_auth.py`<br>`test_database.py` |
| **User Preferences** | `user_preferences` | `UserPreference` (`models/user_preference.py`) | Handled via `UserRepository` | `GET /api/v1/auth/me` | `test_database.py` |
| **Language Catalog** | `languages` | `Language` (`models/language.py`) | Direct via `VoiceService` | `GET /api/v1/languages` | `test_voices.py`<br>`test_database.py` |
| **Dynamic Voices** | `voices` | `Voice` (`models/voice.py`) | Direct via `VoiceService` | `GET /api/v1/voices`<br>`POST /api/v1/voices` | `test_voices.py`<br>`test_database.py` |
| **Speech Generations** | `speech_generations`| `SpeechGeneration` (`models/speech_generation.py`)| `SpeechGenerationRepository` (`repositories/speech_generation.py`) | `POST /api/v1/tts` | `test_tts.py`<br>`test_database.py` |
| **Speech History** | `speech_generations`| `SpeechGeneration` (`models/speech_generation.py`)| `SpeechGenerationRepository` (`repositories/speech_generation.py`) | `GET /api/v1/history` | `test_tts.py`<br>`test_database.py` |
| **Bookmarked Favorites**| `favorites` | `Favorite` (`models/favorite.py`) | `FavoriteRepository` (`repositories/favorite.py`) | `GET /api/v1/favorites`<br>`POST /api/v1/favorites` | `test_database.py` |
| **Quantum Experiments** | `quantum_experiments`| `QuantumExperiment` (`models/quantum_experiment.py`)| `QuantumExperimentRepository` (`repositories/quantum_experiment.py`)| `POST /api/v1/quantum/circuit`<br>`GET /api/v1/quantum/history` | `test_quantum.py`<br>`test_database.py` |

