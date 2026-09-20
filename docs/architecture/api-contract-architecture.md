# Bloop REST API & Schema Contract Architecture Specification

## 1. Architectural Overview

The **Bloop API Contract Architecture** establishes a rigid, type-safe, and deterministic communication protocol between the React/TypeScript frontend application and the asynchronous FastAPI backend server. Operating over versioned `/api/v1` routes, this contract isolates clients from proprietary vendor SDKs, decouples quantum intelligence operations, strictly enforces resource ownership boundaries, and guarantees zero credential leakage.

---

## 2. End-to-End API Architecture

```mermaid
graph TD
    subgraph ClientLayer ["Client Layer (React / TypeScript)"]
        UI["Bloop Web Interface"]
        TQ["TanStack Query Cache"]
        Axios["Axios / Fetch HTTP Client"]
        UI --> TQ
        TQ --> Axios
    end

    subgraph EdgeMiddleware ["FastAPI Middleware Pipeline"]
        CORS["CORS Middleware"]
        ReqID["Request ID Tracker (X-Request-ID)"]
        SecHeaders["Security Headers Middleware"]
        Timing["Timing Middleware (X-Process-Time)"]
        PayloadLimit["Payload Size Enforcer (10MB)"]
        Axios --> CORS
        CORS --> ReqID
        ReqID --> SecHeaders
        SecHeaders --> Timing
        Timing --> PayloadLimit
    end

    subgraph RoutingAndContracts ["API Routing & Contract Enforcement"]
        Pydantic["Pydantic v2 Validation"]
        AuthDep["JWT Bearer Auth Dependency"]
        Router["APIRouter (/api/v1)"]
        PayloadLimit --> Pydantic
        Pydantic --> AuthDep
        AuthDep --> Router
    end

    subgraph Domains ["Domain Subsystems"]
        AuthService["Auth & Identity Service"]
        UserService["User & Preference Service"]
        CatalogService["Language & Dynamic Voice Registry"]
        TTSService["Speech Synthesis Engine"]
        QuantumService["Decoupled Quantum Engine"]
        AuditService["History & Favorite Repositories"]

        Router -->|/auth| AuthService
        Router -->|/users| UserService
        Router -->|/languages & /voices| CatalogService
        Router -->|/tts| TTSService
        Router -->|/quantum| QuantumService
        Router -->|/history & /favorites| AuditService
    end

    subgraph DataAndStorage ["Persistence & External Providers"]
        Postgres[(PostgreSQL 16 DB)]
        AudioStorage["Local / S3 Audio Cache"]
        ElevenLabs["ElevenLabs Voice API (Server Only)"]
        QiskitSim["Qiskit / Aer Quantum Simulator"]

        AuthService --> Postgres
        UserService --> Postgres
        CatalogService --> Postgres
        AuditService --> Postgres
        TTSService --> AudioStorage
        TTSService --> ElevenLabs
        TTSService -.->|Acoustic Vectors| QuantumService
        QuantumService --> QiskitSim
    end
```

---

## 3. Request-Response Lifecycle

```mermaid
sequenceDiagram
    autonumber
    actor User as Client (React/TS)
    participant MW as Middleware Pipeline
    participant Dep as Dependencies (Auth / DB)
    participant End as API Endpoint Handler
    participant Svc as Domain Service
    participant Repo as SQLAlchemy Repository
    participant DB as PostgreSQL Database

    User->>MW: HTTP Request (Headers, JWT, Payload)
    MW->>MW: Generate/Sanitize X-Request-ID, Start Timer
    MW->>Dep: Inject Database Session & Validate JWT
    alt Invalid or Expired Token
        Dep-->>MW: Raise AuthenticationException
        MW-->>User: 401 Unauthorized (Error Envelope)
    else Authenticated
        Dep->>End: Pass CurrentUser & Session
        End->>End: Validate Pydantic Schema
        End->>Svc: Execute Business Logic
        Svc->>Repo: Query / Mutate Entity
        Repo->>DB: SQL Transaction (Atomic)
        DB-->>Repo: Database Result
        Repo-->>Svc: Domain Model
        Svc-->>End: Result Payload
        End-->>MW: Format ApiResponse[T] Envelope
        MW->>MW: Append Security & X-Process-Time Headers
        MW-->>User: HTTP 200/201 (Standard JSON Envelope)
    end
```

---

## 4. Error Flow & Production Sanitization

```mermaid
flowchart TD
    ExcStart["Exception Raised in Application"] --> ExcType{"Exception Type?"}

    ExcType -->|Text / Payload / Capability Error| ValHandler["Validation Exception Handler"]
    ValHandler --> Envelope422["HTTP 422: TEXT_EMPTY / TEXT_TOO_LONG / INVALID_LANGUAGE / INVALID_VOICE / VOICE_LANGUAGE_MISMATCH / VALIDATION_ERROR"]

    ExcType -->|Custom Bloop Domain Exception| BloopHandler["BloopException Handler"]
    BloopHandler --> StatusMap{"Domain Status Code"}
    StatusMap -->|401| Envelope401["HTTP 401: AUTHENTICATION_REQUIRED / INVALID_CREDENTIALS"]
    StatusMap -->|403| Envelope403["HTTP 403: ACCESS_DENIED / FORBIDDEN"]
    StatusMap -->|404| Envelope404["HTTP 404: RESOURCE_NOT_FOUND / LANGUAGE_NOT_FOUND / VOICE_NOT_FOUND"]
    StatusMap -->|409| Envelope409["HTTP 409: RESOURCE_CONFLICT / CONFLICT"]
    StatusMap -->|429| Envelope429["HTTP 429: RATE_LIMIT_EXCEEDED"]
    StatusMap -->|502| Envelope502["HTTP 502: TTS_PROVIDER_UNAVAILABLE / PROVIDER_ERROR"]
    StatusMap -->|503| Envelope503["HTTP 503: QUANTUM_DISABLED"]

    ExcType -->|SQLAlchemy / Database Error| DBHandler["SQLAlchemyError Handler"]
    DBHandler --> Rollback["db.rollback()"]
    Rollback --> LogTrace["Log Full Stack Trace Server-Side"]
    LogTrace --> Envelope500DB["HTTP 500: Sanitized DATABASE_ERROR (No Table/Schema Leak)"]

    ExcType -->|Unhandled Python Exception| RootHandler["Global 500 Handler"]
    RootHandler --> LogUnhandled["Log Full Trace Server-Side"]
    LogUnhandled --> Envelope500Root["HTTP 500: Sanitized INTERNAL_SERVER_ERROR"]

    Envelope422 --> ClientResponse["Return Uniform JSON Error Envelope to Client"]
    Envelope401 --> ClientResponse
    Envelope403 --> ClientResponse
    Envelope404 --> ClientResponse
    Envelope409 --> ClientResponse
    Envelope429 --> ClientResponse
    Envelope502 --> ClientResponse
    Envelope503 --> ClientResponse
    Envelope500DB --> ClientResponse
    Envelope500Root --> ClientResponse
```

---

## 5. Resource Ownership Boundary

```mermaid
flowchart TD
    ClientReq["Client Request to Protected Resource"] --> ExtractUser["Extract Current User from Bearer Token"]
    ExtractUser --> CheckSuperuser{"Is User Superuser?"}

    CheckSuperuser -->|Yes| GrantAccess["Grant Cross-Tenant Access"]
    CheckSuperuser -->|No| FetchResource["Fetch Target Entity from DB"]

    FetchResource --> ExistsCheck{"Entity Exists?"}
    ExistsCheck -->|No| Raise404["Raise ResourceNotFoundException (404)"]

    ExistsCheck -->|Yes| OwnershipCheck{"resource.user_id == current_user.id?"}
    OwnershipCheck -->|Yes| AllowAction["Allow Query, Update, or Delete"]
    OwnershipCheck -->|No| Raise403["Raise AuthorizationException (403 ACCESS_DENIED)"]

    AllowAction --> ReturnSuccess["Return Scoped Resource Payload"]
    Raise404 --> ReturnError["Return 404 Error Envelope"]
    Raise403 --> DenyAccess["Block Action & Return 403 Error Envelope"]
```

---

## 6. Architectural Guarantees Summary

1. **Zero Secret Exposure:** Vendor credentials (e.g. `ELEVENLABS_API_KEY`) and cryptographic keys (`JWT_SECRET_KEY`) never cross the API boundary.
2. **Provider Voice ID Abstraction:** Raw vendor voice IDs (e.g. ElevenLabs ID) are strictly isolated in `provider_voice_id` and never serialized to client responses.
3. **Dynamic Voice Registry:** Voices are resolved dynamically through database and capability discovery, ensuring zero proprietary voice names or IDs are hardcoded in frontend contracts.
4. **Authoritative Capability Validation:** The backend enforces Level 3 capability validation (language existence, voice existence, and voice-language compatibility) before any provider execution is initiated.
5. **Decoupled Quantum Engine:** Quantum analysis runs independently. If disabled, callers receive a graceful 503 while audio synthesis operates normally via fallback modulation.
6. **Tenant Isolation:** Multi-user isolation is enforced at the repository and route dependency level, preventing unauthorized access across user generation histories and favorites.
