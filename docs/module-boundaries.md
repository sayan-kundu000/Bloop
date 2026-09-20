# Bloop — Module Boundaries & Interface Contracts

**Document Identifier:** BLOOP-BOUNDARIES-V1  
**Project:** Bloop — AI Text-to-Speech & Quantum Intelligence Platform  
**Target Milestone:** Intermediate-Level Architecture  
**Status:** Approved Technical Design  
**Authority:** Bloop Master Prompt & Prompt 02

---

## 1. Architectural Layering & Separation of Concerns

Bloop strictly enforces unidirectional dependencies between Clean Architecture layers. Cross-layer violations (e.g., database queries inside an API router or direct third-party HTTP requests in a repository) are strictly prohibited.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MODULE BOUNDARY HIERARCHY                          │
├───────────────────────┬─────────────────────────────────────────────────────┤
│ 1. Presentation Layer │ React 19, TypeScript, Tailwind, TanStack Query, UI  │
│ 2. API Routing Layer  │ FastAPI APIRouters, Pydantic v2 Schemas, Dependency │
│ 3. Service Layer      │ TTSService, VoiceService, AuthService, QuantumService│
│ 4. Provider Layer     │ BaseTTSProvider, ElevenLabsProvider, SimProvider    │
│ 5. Repository Layer   │ UserRepository, VoiceRepository, GenerationRepo     │
│ 6. Persistence Layer  │ SQLAlchemy 2.0 ORM, Alembic Migrations, PostgreSQL  │
│ 7. Quantum Layer      │ Qiskit Aer, PennyLane, Scikit-Learn Benchmarks      │
└───────────────────────┴─────────────────────────────────────────────────────┘
```

---

## 2. Interface Contracts & Type Signatures

### 2.1 Provider Abstraction Layer (`backend/app/providers/base.py`)

The core TTS pipeline depends solely on the abstract provider interface, isolating the application from external vendor SDK changes:

```python
from abc import ABC, abstractmethod
from typing import BinaryIO, Optional, Dict, Any

class BaseTTSProvider(ABC):
    """Abstract Base Class for Text-to-Speech Providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the unique identifier of the provider."""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Returns True if the provider has all required credentials and is ready."""
        pass

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        voice_id: str,
        options: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Synthesizes speech from text.
        
        Args:
            text: The text to convert to speech (1 <= len <= 2500).
            voice_id: The target voice identifier.
            options: Provider-specific options (stability, similarity_boost, etc.).
            
        Returns:
            Raw audio file bytes (MPEG-3).
            
        Raises:
            ProviderError: If the external service fails or returns an error.
            ProviderTimeoutError: If the provider call exceeds the timeout threshold.
        """
        pass
```

---

### 2.2 Application Service Layer (`backend/app/services/`)

#### TTSService (`backend/app/services/tts_service.py`)
```python
class TTSService:
    def __init__(self, db: Session, provider: BaseTTSProvider):
        self.db = db
        self.provider = provider
        self.voice_repo = VoiceRepository(db)
        self.generation_repo = SpeechGenerationRepository(db)

    async def synthesize_speech(
        self,
        user_id: int,
        request: TTSRequest
    ) -> TTSResponse:
        """
        Orchestrates speech synthesis:
        1. Validates text length and content.
        2. Verifies voice existence and language compatibility.
        3. Calls provider (ElevenLabs or Simulation).
        4. Persists audio file to disk storage.
        5. Records generation record in database.
        6. Returns structured response with streaming URLs.
        """
        pass

    def get_audio_stream(
        self,
        filename: str,
        range_header: Optional[str] = None
    ) -> StreamingResponse:
        """
        Streams audio file supporting HTTP 206 Partial Content / Range requests.
        """
        pass
```

#### VoiceService (`backend/app/services/voice_service.py`)
```python
class VoiceService:
    def __init__(self, db: Session):
        self.db = db
        self.voice_repo = VoiceRepository(db)

    def get_voices(
        self,
        language_code: Optional[str] = None,
        gender: Optional[str] = None
    ) -> List[VoiceResponse]:
        """Queries active voices matching optional filters."""
        pass

    def register_custom_voice(
        self,
        voice_in: VoiceCreate
    ) -> VoiceResponse:
        """Injects a user-supplied ElevenLabs voice ID into the database registry."""
        pass

    def import_voices_from_config(self) -> Dict[str, int]:
        """Reads backend/voices_config.json and batch upserts voices into DB."""
        pass
```

#### QuantumService (`backend/app/services/quantum_service.py`)
```python
class QuantumService:
    def __init__(self, db: Session):
        self.db = db

    async def classify_text_vqc(
        self,
        text: str
    ) -> QuantumTextResponse:
        """Runs Qiskit Aer VQC and classical baseline for text style."""
        pass

    async def analyze_emotion_qnn(
        self,
        text: str
    ) -> QuantumEmotionResponse:
        """Executes PennyLane Hybrid QNN for affective wire expectation values."""
        pass

    async def compute_semantic_fidelity(
        self,
        text_a: str,
        text_b: str
    ) -> QuantumSemanticResponse:
        """Calculates quantum state overlap fidelity between two prompts."""
        pass

    async def run_circuit_simulation(
        self,
        circuit_def: CircuitDefinition
    ) -> CircuitResultResponse:
        """Simulates arbitrary gate configurations with optional decoherence noise."""
        pass

    async def execute_benchmark(
        self,
        dataset_id: str,
        shots: int = 1024
    ) -> BenchmarkResponse:
        """Runs controlled classical vs quantum comparison without supremacy bias."""
        pass
```

---

## 3. Dependency Injection & Inversion of Control (IoC)

FastAPI's dependency injection system (`Depends`) manages lifecycle and decoupling across all endpoints:

```python
# Database Session Injection
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Provider Injection with Automatic Fallback
def get_tts_provider() -> BaseTTSProvider:
    if settings.ELEVENLABS_API_KEY:
        return ElevenLabsProvider(
            api_key=settings.ELEVENLABS_API_KEY,
            api_base=settings.ELEVENLABS_API_BASE
        )
    return SimulationTTSProvider()

# Service Injection
def get_tts_service(
    db: Session = Depends(get_db),
    provider: BaseTTSProvider = Depends(get_tts_provider)
) -> TTSService:
    return TTSService(db=db, provider=provider)

# User Authentication Injection
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    return AuthService(db).validate_token_and_get_user(token)
```

---

## 4. Error Boundaries & Fault Containment

### The Decoupling Boundary
* **Rule:** An unhandled exception or crash inside `QuantumService` must **never** bubble up to affect `TTSService` or crash the application worker process.
* **Mechanism:** All quantum operations are wrapped in an error-handling boundary:
  ```python
  try:
      return await self._run_aer_simulation(...)
  except Exception as e:
      logger.error(f"Quantum simulation error: {e}", exc_info=True)
      raise QuantumExecutionException(
          code="QUANTUM_EXECUTION_ERROR",
          message="Quantum simulation failed. Core speech services remain operational."
      )
  ```

### Provider Fault Isolation Boundary
* **Rule:** ElevenLabs network drops, 429 rate limits, or HTTP 500 errors must never expose internal vendor credentials, connection strings, or raw stack traces to the client.
* **Mechanism:** `ElevenLabsProvider` traps all `httpx.HTTPError` exceptions and maps them to clean application errors (`ProviderException`), which the global exception handler wraps in a safe `HTTP 502 {"code": "PROVIDER_ERROR"}` JSON envelope.

---

## 5. Testing Boundaries & Mocking Strategy

| Test Layer | Target Module | Mocking Strategy | Verification Tool |
| :--- | :--- | :--- | :--- |
| **Unit Tests** | Services, Quantum Engines | Mock database session; mock `BaseTTSProvider` | Pytest |
| **Integration Tests** | API Endpoints (`/api/v1/*`) | SQLite in-memory database; `SimulationTTSProvider` | FastAPI TestClient |
| **Provider Tests** | `ElevenLabsProvider` | Mock HTTP responses (`pytest-httpx` / `responses`) | Pytest |
| **Frontend Tests** | Components, Stores | Mock Axios responses (`msw` or Vitest mocks) | Vitest + React Testing Library |
| **E2E Smoke Tests** | Live Deployed System | Live `/api/v1/health` heartbeat and test credentials | Postman / Pytest |
