# Bloop Backend Architecture

## 1. Overview

The Bloop backend is built as an intermediate-level, production-grade **FastAPI** application operating on Python 3.12+. It serves as the single authoritative API runtime for the Bloop AI Text-to-Speech & Quantum Intelligence Platform.

Governing Runtime Principles:
- **FastAPI Owns the API Runtime**: Application lifecycle, routing, request parsing, dependency injection, middleware execution, exception handling, and OpenAPI documentation generation.
- **Router ≠ Business Logic**: Route handlers are strictly thin coordination layers delegating to domain services, repositories, and provider adapters.
- **Security Authority**: The backend is the sole security boundary; client claims, text lengths, and ownership are validated server-side.
- **Provider & Quantum Decoupling**: External provider calls (ElevenLabs) and Quantum Computing simulations (Qiskit/PennyLane) are isolated from core API runtime health.

---

## 2. System Architecture Diagram

```mermaid
graph TD
    Client["React Frontend (Vercel)"]
    Gateway["HTTPS / TLS Gateway (Render)"]
    Uvicorn["Uvicorn ASGI Server"]
    FastAPIApp["FastAPI Application (create_app)"]

    subgraph "Middleware Pipeline"
        CORS["1. CORS Middleware"]
        PayloadLimit["2. Payload Limit Middleware"]
        RequestID["3. Request ID Middleware"]
        SecHeaders["4. Security Headers Middleware"]
        Timing["5. Request Timing & Logging"]
    end

    subgraph "API Layer (/api/v1)"
        HealthR["Health Router"]
        AuthR["Auth Router"]
        UsersR["Users Router"]
        LangR["Languages Router"]
        VoiceR["Voices Router"]
        TTSR["Speech / TTS Router"]
        HistR["History Router"]
        FavR["Favorites Router"]
        QuantumR["Quantum Router"]
    end

    subgraph "Service Layer"
        AuthSvc["Auth Service"]
        VoiceSvc["Voice Service"]
        TTSSvc["TTS Service"]
        AudioDSP["Audio DSP Engine"]
        QuantumSvc["Quantum Service"]
    end

    subgraph "Persistence & Providers"
        UserRepo["User Repository"]
        SpeechRepo["Speech Repository"]
        FavRepo["Favorite Repository"]
        QuantumRepo["Quantum Repository"]
        DB[(PostgreSQL 16)]
        ElevenLabs[("ElevenLabs REST API")]
        QiskitEngine["Qiskit / PennyLane Simulators"]
    end

    Client -->|HTTPS / JSON| Gateway
    Gateway --> Uvicorn
    Uvicorn --> FastAPIApp
    FastAPIApp --> CORS
    CORS --> PayloadLimit
    PayloadLimit --> RequestID
    RequestID --> SecHeaders
    SecHeaders --> Timing
    Timing --> HealthR & AuthR & UsersR & LangR & VoiceR & TTSR & HistR & FavR & QuantumR

    AuthR --> AuthSvc --> UserRepo --> DB
    UsersR --> UserRepo
    VoiceR --> VoiceSvc --> DB
    TTSR --> TTSSvc --> AudioDSP
    TTSSvc --> ElevenLabs
    TTSSvc --> SpeechRepo --> DB
    HistR --> SpeechRepo
    FavR --> FavRepo --> DB
    QuantumR --> QuantumSvc --> QiskitEngine
    QuantumSvc --> QuantumRepo --> DB
```

---

## 3. Request Lifecycle Diagram

```mermaid
sequenceDiagram
    autonumber
    actor Client as React Client
    participant MW as Middleware Pipeline
    participant Router as API Router (/api/v1)
    participant DI as Dependency Injection
    participant Svc as Domain Service
    participant Repo as Repository / Provider
    participant DB as PostgreSQL 16

    Client->>MW: HTTP Request (Headers + Body)
    Note over MW: Evaluates CORS Origin<br/>Enforces 2MB Content-Length<br/>Generates/Validates X-Request-ID<br/>Starts perf timer
    MW->>Router: Dispatched Request
    Router->>DI: Resolve Dependencies
    Note over DI: get_db() -> Session<br/>get_current_user() -> JWT Auth<br/>get_settings()
    DI->>Router: Injected Dependencies
    Router->>Svc: Invoke Business Operation
    Svc->>Repo: Execute Query / Provider Call
    Repo->>DB: SQL Transaction (select/insert)
    DB-->>Repo: Query Result
    Repo-->>Svc: Domain Model
    Svc-->>Router: Response DTO
    Router-->>MW: JSONResponse / Pydantic Schema
    Note over MW: Attaches X-Request-ID<br/>Attaches Security Headers<br/>Calculates X-Response-Time<br/>Emits Access Log
    MW-->>Client: HTTP Response (200 OK + Headers)
```

---

## 4. Layer Responsibilities & Boundaries

| Layer | Primary Responsibility | Prohibited Actions |
| :--- | :--- | :--- |
| **`app.factory`** | Application assembly, lifespan context, middleware registration | Business logic, direct DB queries |
| **`app.core.middleware`** | Cross-cutting HTTP headers, timing, correlation, security | Database access, user authentication |
| **`app.core.exceptions`** | Exception definitions, sanitized error serialization | Traceback exposure to clients |
| **`app.api.router`** | Route composition under `/api/v1` | Business logic |
| **`app.api.v1.endpoints`** | HTTP contract, parameter validation, DI invocation | SQL queries, raw provider HTTP calls |
| **`app.services`** | Domain business workflows, orchestration | Direct FastAPI route registration |
| **`app.repositories`** | Database queries, SQLAlchemy 2.x persistence | HTTP response creation |
| **`app.providers`** | External vendor adapters (ElevenLabs) | Database access |
| **`app.quantum`** | Quantum circuit simulation & modeling | Core TTS pipeline blocking |
