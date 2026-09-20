# Bloop — Backend Architecture Specification

**Document Identifier:** BLOOP-BACKEND-ARCH-V1  
**Project:** Bloop — AI Text-to-Speech & Quantum Intelligence Platform  
**Target Milestone:** Intermediate-Level Backend Architecture  
**Status:** Approved Technical Design  
**Authority:** Bloop Master Prompt & Prompt 02  

---

## 1. Executive Backend Overview

The Bloop backend is a modern, asynchronous web application developed using **Python 3.11+**, **FastAPI**, **Pydantic v2**, **SQLAlchemy 2.0**, and **Alembic**. It provides high-throughput RESTful APIs, strict request validation, commercial AI speech synthesis mediation via ElevenLabs, multi-tenant relational persistence, and an isolated in-process Quantum Intelligence engine (Qiskit & PennyLane).

```
HTTP Request
     │
     ▼
FastAPI App (main.py)
     │
     ▼
APIRouter (/api/v1/*) ──► Pydantic v2 Schemas (Validation)
     │
     ▼
Dependencies (get_current_user, get_db)
     │
     ▼
Business Service Layer (TTSService, AuthService, VoiceService, QuantumService)
     ├──► Provider Layer (BaseTTSProvider -> ElevenLabsProvider, SimulationProvider)
     │
     ▼
Repository Layer (UserRepository, GenerationRepository, VoiceRepository)
     │
     ▼
Database Layer (SQLAlchemy 2.0 ORM -> PostgreSQL 16)
```

---

## 2. Technology Stack & Ecosystem

| Component | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Web Framework** | FastAPI | 0.115+ | High-performance asynchronous REST API routing and OpenAPI documentation. |
| **ASGI Server** | Uvicorn | 0.30+ | Lightning-fast ASGI web server worker process. |
| **Data Validation** | Pydantic | 2.9+ | Strict input validation, data parsing, and serialization. |
| **ORM & Database** | SQLAlchemy | 2.0+ | Modern type-safe relational mapping and transaction management. |
| **Migrations** | Alembic | 1.13+ | Deterministic database schema versioning and automated migrations. |
| **HTTP Client** | HTTPX | 0.27+ | Asynchronous non-blocking HTTP requests to the ElevenLabs REST API. |
| **Security & Passwords** | Passlib / Bcrypt | Latest | Cryptographically salted password hashing. |
| **Auth Tokens** | PyJWT | 2.9+ | Stateless JWT generation and cryptographic verification. |
| **Quantum Engine** | Qiskit Aer & PennyLane | 0.15+ / 0.38+ | In-process quantum statevector simulation, VQC, and QNN execution. |
| **Testing** | Pytest & pytest-asyncio | 8.x | Comprehensive unit, repository, service, and integration testing. |

---

## 3. Logical Directory Structure

```
backend/
├── alembic/                # Alembic database migrations
│   ├── versions/           # Versioned migration revision scripts
│   └── env.py              # Alembic environment and SQLAlchemy model binding
├── app/
│   ├── api/                # API Routing and dependency injection
│   │   ├── deps.py         # FastAPI dependencies: get_db, get_current_user, get_tts_provider
│   │   └── v1/
│   │       ├── api_router.py  # Central router mounting all endpoint modules
│   │       └── endpoints/
│   │           ├── health.py     # GET /health
│   │           ├── auth.py       # POST /auth/register, /auth/login, GET /auth/me
│   │           ├── tts.py        # POST /tts, GET /tts/audio/{file}, GET /tts/download/{file}
│   │           ├── voices.py     # GET /voices, POST /voices, POST /voices/reload
│   │           ├── languages.py  # GET /languages
│   │           ├── history.py    # GET /history, GET /history/{id}, DELETE /history/{id}
│   │           ├── favorites.py  # GET /favorites, POST /favorites, DELETE /favorites/{id}
│   │           └── quantum.py    # POST /quantum/text, /emotion, /semantic, /circuit, /benchmark
│   │
│   ├── core/               # Application-wide singletons and primitives
│   │   ├── config.py       # Pydantic BaseSettings loading from .env
│   │   ├── security.py     # Bcrypt password hashing, JWT creation & verification
│   │   ├── exceptions.py   # Normalized domain exceptions (BloopException hierarchy)
│   │   └── logging.py      # Structured JSON logging configuration
│   │
│   ├── db/                 # Database connection and session management
│   │   ├── base.py         # Declarative Base importing all models for Alembic
│   │   └── session.py      # SessionLocal engine and get_db generator
│   │
│   ├── models/             # SQLAlchemy ORM database models
│   │   ├── user.py         # User & UserPreference entities
│   │   ├── voice.py        # Voice & Language entities
│   │   ├── speech.py       # SpeechGeneration & Favorite entities
│   │   └── quantum.py      # QuantumExperiment log entity
│   │
│   ├── schemas/            # Pydantic v2 request/response schemas
│   │   ├── envelope.py     # Standard ResponseEnvelope[T] and ErrorEnvelope
│   │   ├── auth.py         # UserRegister, UserLogin, TokenResponse, UserRead
│   │   ├── tts.py          # TTSRequest, TTSResponse, VoiceRead, LanguageRead
│   │   ├── history.py      # HistoryFilterParams, HistoryItemRead, PaginatedHistory
│   │   ├── favorites.py    # FavoriteCreate, FavoriteRead
│   │   └── quantum.py      # Request/Response models for all 5 quantum engines
│   │
│   ├── repositories/       # Encapsulated data access objects
│   │   ├── base.py         # Generic BaseRepository with CRUD helpers
│   │   ├── user_repo.py    # UserRepository
│   │   ├── voice_repo.py   # VoiceRepository & LanguageRepository
│   │   ├── speech_repo.py  # SpeechGenerationRepository
│   │   └── favorite_repo.py# FavoriteRepository
│   │
│   ├── services/           # Business logic and domain orchestrators
│   │   ├── tts_service.py      # Speech synthesis orchestration & audio recording
│   │   ├── auth_service.py     # Authentication, token lifecycle, password validation
│   │   ├── voice_service.py    # Voice registry, language validation, ingestion
│   │   ├── history_service.py  # History querying, multi-filter, pagination, ownership
│   │   ├── favorite_service.py # Bookmark toggle, notes, ownership enforcement
│   │   └── quantum_service.py  # Quantum engine orchestration & result normalization
│   │
│   ├── providers/          # External and synthetic provider adapters
│   │   ├── base.py         # BaseTTSProvider abstract base class
│   │   ├── elevenlabs.py   # ElevenLabsProvider (HTTPX async client)
│   │   └── simulation.py   # SimulationTTSProvider (offline synthetic tone generator)
│   │
│   ├── storage/            # Server disk audio file manager
│   │   └── audio_manager.py # File write, HTTP 206 byte-range seek streamer, cleanup
│   │
│   ├── quantum/            # 5 Isolated Quantum Intelligence Engines
│   │   ├── text_classifier.py  # Lexical extraction + Qiskit 4-qubit VQC
│   │   ├── emotion_qnn.py      # PennyLane 4-wire affective Pauli-Z expectations
│   │   ├── semantic_kernel.py  # Qiskit transition fidelity state overlap
│   │   ├── circuit_lab.py      # Qiskit Aer circuit simulator & noise modeling
│   │   └── benchmarks.py       # Scikit-Learn Logistic Regression vs Qiskit VQC
│   │
│   └── main.py             # FastAPI entrypoint, CORS, exception handlers, middleware
│
├── tests/                  # Automated Pytest suite
│   ├── conftest.py         # Test fixtures, in-memory SQLite DB, client fixture
│   ├── test_auth.py        # Registration, login, token verification tests
│   ├── test_tts.py         # Validation limits, synthesis mock, audio stream tests
│   ├── test_history.py     # Pagination, multi-filter, deletion tests
│   └── test_quantum.py     # Algorithm validation and error isolation tests
│
├── voices_config.json      # File-based dynamic voice ingestion registry
├── requirements.txt        # Production Python dependencies
└── .env                    # Secret environment variables (ignored by Git)
```

---

## 4. Service Layer Responsibilities & Contracts

The Service Layer coordinates business workflows and enforces domain rules:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          BACKEND SERVICE LAYER CONTRACTS                    │
├───────────────────────┬─────────────────────────────────────────────────────┤
│ Service               │ Core Responsibilities                              │
├───────────────────────┼─────────────────────────────────────────────────────┤
│ **TTSService**        │ Validates character bounds (1 to 2500); verifies   │
│                       │ voice compatibility with selected language; passes  │
│                       │ text to BaseTTSProvider; saves audio via            │
│                       │ AudioManager; records metadata in GenerationRepo.   │
├───────────────────────┼─────────────────────────────────────────────────────┤
│ **AuthService**       │ Hashes passwords using bcrypt; verifies credentials;│
│                       │ issues signed JWT tokens; decodes and validates     │
│                       │ Bearer tokens; fetches authenticated user details.  │
├───────────────────────┼─────────────────────────────────────────────────────┤
│ **VoiceService**      │ Retrieves active voices filtered by ISO language;   │
│                       │ registers dynamic voices (UI / JSON config);        │
│                       │ enforces zero hardcoded vendor voice rule.          │
├───────────────────────┼─────────────────────────────────────────────────────┤
│ **HistoryService**    │ Applies multi-parametric filters (search, voice,    │
│                       │ language, dates); enforces strict tenant ownership; │
│                       │ returns paginated history; deletes generations.     │
├───────────────────────┼─────────────────────────────────────────────────────┤
│ **FavoriteService**   │ Toggles bookmark state on speech generations;       │
│                       │ verifies generation ownership; adds custom notes.   │
├───────────────────────┼─────────────────────────────────────────────────────┤
│ **QuantumService**    │ Dispatches feature vectors to Qiskit / PennyLane    │
│                       │ engines; enforces execution timeouts and limits     │
│                       │ (qubits <= 8, shots <= 1024); normalizes results.   │
└───────────────────────┴─────────────────────────────────────────────────────┘
```

---

## 5. Repository Layer & Data Isolation

All database queries are encapsulated in repository classes. To guarantee multi-tenant security, queries for user-owned records **must** enforce tenant boundaries:

```python
class SpeechGenerationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id_and_user(self, generation_id: int, user_id: int) -> Optional[SpeechGeneration]:
        """Strictly ensures a user can only access their own generation record."""
        stmt = select(SpeechGeneration).where(
            SpeechGeneration.id == generation_id,
            SpeechGeneration.user_id == user_id
        )
        return self.db.scalars(stmt).first()
```

---

## 6. Provider Abstraction Layer

The application interacts with Text-to-Speech hardware exclusively through the `BaseTTSProvider` interface:

```python
class BaseTTSProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        pass

    @abstractmethod
    async def synthesize(self, text: str, voice_id: str, options: Optional[dict] = None) -> bytes:
        pass
```

### Provider Implementations:
1. **`ElevenLabsProvider` (`providers/elevenlabs.py`):**
   - Communicates with `https://api.elevenlabs.io/v1/text-to-speech/{voice_id}`.
   - Attaches `xi-api-key` header loaded from `settings.ELEVENLABS_API_KEY`.
   - Uses `httpx.AsyncClient` with a 30-second timeout.
   - Translates HTTP 401, 429, and connection errors into normalized domain exceptions.
2. **`SimulationTTSProvider` (`providers/simulation.py`):**
   - Automatically selected if `ELEVENLABS_API_KEY` is not provided.
   - Synthesizes an offline sinusoidal audio waveform encoded in valid MP3 format.
   - Enables full automated testing and offline development without external API costs.

---

## 7. Global Exception Architecture & Error Normalization

Bloop intercepts all runtime exceptions and formats them into a standard JSON envelope:

```python
# Standardized Error Envelope
{
    "success": false,
    "error": {
        "code": "INVALID_TEXT_LENGTH",
        "message": "Text length must be between 1 and 2,500 characters.",
        "details": {"current_length": 3100, "max_length": 2500}
    }
}
```

### Error Code Taxonomy:
- `400 Bad Request`: `EMPTY_TEXT`, `TEXT_TOO_LONG`, `VOICE_LANGUAGE_MISMATCH`, `INVALID_VOICE_ID`.
- `401 Unauthorized`: `INVALID_CREDENTIALS`, `TOKEN_EXPIRED`, `UNAUTHORIZED`.
- `403 Forbidden`: `FORBIDDEN_RESOURCE_ACCESS`.
- `404 Not Found`: `USER_NOT_FOUND`, `VOICE_NOT_FOUND`, `GENERATION_NOT_FOUND`.
- `422 Unprocessable Entity`: `SCHEMA_VALIDATION_ERROR`.
- `429 Too Many Requests`: `RATE_LIMIT_EXCEEDED`, `PROVIDER_QUOTA_EXCEEDED`.
- `502 / 503 Bad Gateway`: `PROVIDER_UNAVAILABLE`, `PROVIDER_TIMEOUT`.
- `500 Internal Error`: `QUANTUM_EXECUTION_ERROR`, `INTERNAL_SERVER_ERROR`.

---

## 8. Security & Authentication Architecture

1. **Password Storage:** Uses `passlib.context.CryptContext(schemes=["bcrypt"])`. Plaintext passwords never enter logs or database tables.
2. **Stateless JWT Tokens:** Encoded using `pyjwt` with HMAC-SHA256 (`HS256`) and a 24-hour expiration (`exp` claim).
3. **Dependency Injection Guard (`deps.py`):**
   ```python
   async def get_current_user(
       token: str = Depends(oauth2_scheme),
       db: Session = Depends(get_db)
   ) -> User:
       # Validates signature, verifies expiration, queries User from DB
   ```
4. **Secret Isolation:** Environment secrets (`SECRET_KEY`, `ELEVENLABS_API_KEY`, `DATABASE_URL`) are loaded into typed `Settings` using Pydantic `BaseSettings`. No secrets are accessible from client code.

---

## 9. Observability & Health Probes

Bloop exposes a dual-purpose health endpoint at `GET /api/v1/health`:
- **Liveness Probe:** Confirms the FastAPI process is responsive (HTTP 200).
- **Readiness Probe:** Executes a lightweight query against PostgreSQL (`SELECT 1`) and verifies ElevenLabs provider configuration status:
  ```json
  {
      "success": true,
      "data": {
          "status": "healthy",
          "database": "connected",
          "tts_provider": "elevenlabs",
          "quantum_ready": true,
          "version": "1.0.0"
      }
  }
  ```
