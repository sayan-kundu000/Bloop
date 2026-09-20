# Bloop AI — Environment Configuration, Secrets Management & Profiles Architecture

**Document Identifier:** BLOOP-ARCH-ENV-006  
**Status:** Approved Technical Architecture Contract  
**Authority:** Prompt 06 — Environment Configuration, Secrets Management & Development/Production Profiles  
**Core Principle:**
> **Same codebase, different configuration — never different source code for different environments.**

---

## 1. Executive Overview

Bloop enforces a strict Twelve-Factor configuration architecture across all deployment environments:
```text
LOCAL DEVELOPMENT
       ↓
TESTING (CI/CD)
       ↓
PRODUCTION (RENDER & VERCEL)
```
No code modifications, feature flags in source files, or manual URL changes are permitted between environments. Application code strictly consumes configuration provided by the centralized configuration layer.

---

## 2. Configuration Flow Architecture

The following Mermaid diagram details how configuration flows from raw environment variables through typed layers to application services, maintaining strict separation of concerns:

```mermaid
flowchart TD
    subgraph EnvSources [Environment Variable Sources]
        LocalEnv[".env (Local Workstation)"]
        CIEnv["CI/CD Runner Variables"]
        RenderEnv["Render Dashboard Environment"]
        VercelEnv["Vercel Project Variables"]
    end

    subgraph ConfigLayer [Bloop Centralized Configuration Layer]
        BackendSettings["backend/app/core/config.py\n(Settings - Pydantic BaseSettings)"]
        FrontendConfig["frontend/src/app/config.ts\n(AppConfig - Typed & Frozen)"]
    end

    subgraph BackendConsumers [Backend Runtime Services]
        FastAPIApp["FastAPI ASGI Core"]
        DBSession["SQLAlchemy / DB Engine"]
        SecurityService["JWT & Auth Security"]
        ElevenLabsProv["ElevenLabs TTS Provider"]
        QuantumEngine["Quantum Intelligence Engine"]
        LoggingPipeline["SecretMaskingFilter & Logger"]
    end

    subgraph FrontendConsumers [Frontend Client Services]
        AxiosClient["Axios HTTP Client"]
        ReactApp["React 19 SPA & Components"]
    end

    LocalEnv --> BackendSettings
    CIEnv --> BackendSettings
    RenderEnv --> BackendSettings
    VercelEnv --> FrontendConfig
    LocalEnv --> FrontendConfig

    BackendSettings --> FastAPIApp
    BackendSettings --> DBSession
    BackendSettings --> SecurityService
    BackendSettings --> ElevenLabsProv
    BackendSettings --> QuantumEngine
    BackendSettings --> LoggingPipeline

    FrontendConfig --> AxiosClient
    FrontendConfig --> ReactApp
```

---

## 3. Secret Isolation & Flow Architecture

To guarantee zero secret leakage, secrets are strictly backend-only. The frontend browser bundle receives zero credentials or database URLs.

```mermaid
sequenceDiagram
    autonumber
    actor User as User Browser / React SPA
    participant Vercel as Vercel Edge CDN
    participant Render as Render Web Service (FastAPI)
    participant RenderDB as Render PostgreSQL 16
    participant ElevenLabs as ElevenLabs Cloud API

    Note over User,Vercel: Only Public Variables (VITE_API_BASE_URL)
    User->>Vercel: Load React 19 Client Bundle
    Vercel-->>User: Static HTML / JS (Zero Secrets)
    
    Note over User,Render: Standard REST API Calls (Bearer JWT)
    User->>Render: POST /api/v1/tts (Speech Request)
    
    Note over Render,ElevenLabs: Backend-Only Secret Consumption
    Render->>Render: Load Settings (JWT_SECRET_KEY, ELEVENLABS_API_KEY, DATABASE_URL)
    Render->>RenderDB: Authenticate User & Check Quota
    RenderDB-->>Render: Verified Session
    Render->>ElevenLabs: Synthesize Audio (Authorization: xi-api-key)
    ElevenLabs-->>Render: Raw Audio Stream
    Render-->>User: Synthesized Audio URL & Metadata
```

---

## 4. Frontend / Backend Configuration Boundary

```mermaid
flowchart LR
    subgraph FrontendBoundary [FRONTEND BOUNDARY - Public Only]
        direction TB
        VITE_API_BASE_URL["VITE_API_BASE_URL\n(Backend REST API endpoint)"]
        AppConfig["AppConfig\n(Frozen Immutability)"]
        AuditCheck["Runtime Secret Leak Audit"]
    end

    subgraph SecurityPerimeter [AIR GAP / NETWORK BOUNDARY]
        style SecurityPerimeter fill:#ffebee,stroke:#c62828,stroke-width:2px
        Firewall["CORS & TLS 1.3 Strict Enforcement"]
    end

    subgraph BackendBoundary [BACKEND BOUNDARY - Private & Secrets]
        direction TB
        DATABASE_URL["DATABASE_URL (PostgreSQL URI)"]
        JWT_SECRET_KEY["JWT_SECRET_KEY (HMAC-SHA256)"]
        ELEVENLABS_API_KEY["ELEVENLABS_API_KEY (Vendor Key)"]
        PrivateSettings["Private Settings (CORS, Rate Limits, Quantum, Log Level)"]
    end

    FrontendBoundary --- SecurityPerimeter --- BackendBoundary
```

---

## 5. Environment Profiles Specification

Bloop defines exactly three canonical runtime profiles:

| Vector | `development` | `test` | `production` |
| :--- | :--- | :--- | :--- |
| **Target Infrastructure** | Local developer machine | Local pytest & GitHub Actions | Render Web Service + Vercel Edge |
| **`APP_DEBUG`** | `True` (Interactive tracebacks) | `False` | `False` (Enforced startup invariant) |
| **Database Engine** | SQLite 3 (`bloop.db`) or local PG | Isolated test SQLite (`test_bloop.db`) | Render Managed PostgreSQL 16 |
| **Production DB Protection**| Allowed if configured | **FAIL-FAST: Rejects production DB** | Required persistent PostgreSQL |
| **Authentication Secret** | Insecure local placeholder allowed | Deterministic test secret | Cryptographic 64-char Hex (>=32 chars) |
| **ElevenLabs Provider** | Optional (SimulationTTS fallback) | Mock / Offline simulation | Verified live vendor API Key |
| **CORS Policy** | Permissive localhost (`5173`, `3000`) | Isolated test mock | Strictly locked to Vercel production domain |
| **Logging Profile** | `DEBUG` / `INFO` (Human-readable) | `INFO` / `WARNING` (Deterministic) | `INFO` with `SecretMaskingFilter` |
| **Quantum Intelligence** | Enabled (Simulation shots: 1024) | Enabled (Fast unit tests) | Enabled (Guardrails: 8 qubits, 30s timeout) |

---

## 6. Comprehensive Environment Variable Contract

Every environment variable in Bloop is explicitly typed, classified, and validated:

| Variable Name | Type | Required? | Default | Profile | Classification | Purpose & Constraints |
| :--- | :--- | :---: | :--- | :--- | :---: | :--- |
| `APP_NAME` | `string` | No | `Bloop` | All | Private | Application name in logs, OpenAPI, and health checks. |
| `APP_ENV` | `string` | Yes | `development` | All | Private | Runtime profile: `development`, `test`, `production`. |
| `APP_DEBUG` | `boolean` | No | `true` (dev) | All | Private | Must be `false` in production (rejected at boot if `true`). |
| `APP_VERSION` | `string` | No | `0.1.0` | All | Private | Semantic release version. |
| `API_V1_PREFIX` | `string` | No | `/api/v1` | All | Private | URL prefix namespace for version 1 REST routes. |
| `PORT` | `integer` | No | `8000` | Dev/Prod | Private | Listening port (injected automatically by Render). |
| `DATABASE_URL` | `string` | Prod | `sqlite:///./bloop.db` | All | **Secret** | Connection URI. Production requires PostgreSQL; SQLite is rejected. |
| `JWT_SECRET_KEY` | `string` | Prod | *dev placeholder* | All | **Secret** | HMAC-SHA256 signing secret (min 32 chars in production). |
| `JWT_ALGORITHM` | `string` | No | `HS256` | All | Private | Cryptographic algorithm for JWT generation. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `integer` | No | `1440` | All | Private | Lifetime of access tokens (1440 min = 24h). |
| `ELEVENLABS_API_KEY` | `string` | Prod | `""` | Dev/Prod | **Secret** | ElevenLabs vendor key. If empty, simulation activates. |
| `ELEVENLABS_API_BASE` | `string` | No | `https://api.elevenlabs.io/v1` | Dev/Prod | Private | Base REST URL for ElevenLabs voice generation. |
| `CORS_ORIGINS` | `list/str` | Yes | *Localhost URLs* | All | Private | Allowed CORS origins. Wildcard `*` rejected in production. |
| `RATE_LIMIT_ENABLED` | `boolean` | No | `true` | All | Private | Toggle for rate limiting interceptor. |
| `RATE_LIMIT_PER_MINUTE_TTS` | `integer` | No | `10` | All | Private | Max speech syntheses per minute per user/IP. |
| `RATE_LIMIT_PER_MINUTE_QUANTUM` | `integer` | No | `15` | All | Private | Max quantum executions per minute per user/IP. |
| `RATE_LIMIT_PER_MINUTE_AUTH` | `integer` | No | `5` | All | Private | Max login/register attempts per minute per IP. |
| `AUDIO_STORAGE_PATH` | `string` | No | `backend/app/storage/audio` | All | Private | Filesystem path for generated MP3 audio cache. |
| `QUANTUM_ENABLED` | `boolean` | No | `true` | All | Private | Independent toggle for Quantum subsystem. |
| `QUANTUM_SIMULATOR_SHOTS` | `integer` | No | `1024` | All | Private | Max simulator shots per quantum circuit execution. |
| `QUANTUM_MAX_QUBITS` | `integer` | No | `8` | All | Private | Maximum allowable qubit register size. |
| `QUANTUM_MAX_EXECUTION_TIME` | `integer` | No | `30` | All | Private | Max seconds before circuit execution is terminated. |
| `LOG_LEVEL` | `string` | No | `INFO` | All | Private | Severity threshold: `DEBUG`, `INFO`, `WARNING`, `ERROR`. |
| `VITE_API_BASE_URL` | `string` | Yes | `http://localhost:8000` | Frontend | **Public** | Base URL for Axios client requests. Stripped of trailing slashes. |

---

## 7. Startup Safeguards & Validation Matrix

When the backend initializes, `backend/app/core/config.py` runs `@model_validator(mode="after")` to enforce safety rules:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       FAIL-FAST STARTUP VALIDATION MATRIX                   │
├─────────────────────┬───────────────────┬───────────────────────────────────┤
│ Condition           │ Configuration     │ Startup Behavior                  │
├─────────────────────┼───────────────────┼───────────────────────────────────┤
│ APP_ENV=production  │ APP_DEBUG=True    │ REJECT: Fatal ValueError          │
│ APP_ENV=production  │ JWT_SECRET_KEY <32│ REJECT: Fatal ValueError          │
│ APP_ENV=production  │ Default dev secret│ REJECT: Fatal ValueError          │
│ APP_ENV=production  │ DATABASE_URL=sql..│ REJECT: SQLite forbidden in prod  │
│ APP_ENV=production  │ CORS_ORIGINS=*    │ REJECT: Wildcard forbidden in prod│
│ APP_ENV=test        │ DATABASE_URL=prod │ REJECT: Protects prod database    │
│ All Environments    │ Valid variables   │ BOOT: Success with masked logging │
└─────────────────────┴───────────────────┴───────────────────────────────────┘
```

---

## 8. Quantum Subsystem Failure & Isolation Policy

Quantum Intelligence is an additive, experimental subsystem. 
- Setting `QUANTUM_ENABLED=false` disables quantum routes and circuits without interrupting Core TTS, User Authentication, History, Favorites, or Voice registry.
- Memory and CPU consumption are strictly bounded by `QUANTUM_MAX_QUBITS=8` and `QUANTUM_MAX_EXECUTION_TIME=30s`.

---

## 9. Secret Sanitization & Logging Security

- **Safe String Representation:** `Settings.__repr__()` and `Settings.__str__()` automatically mask database passwords (`postgresql+psycopg2://user:***@host:5432/db`), `JWT_SECRET_KEY` (`***MASKED***`), and `ELEVENLABS_API_KEY` (`***MASKED***`).
- **Logging Filter:** `SecretMaskingFilter` intercepts log records on the root logger and scrubs any occurrences of sensitive credentials from messages and argument tuples, while preserving argument data types for numerical format specifiers.
