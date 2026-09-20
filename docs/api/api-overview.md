# Bloop REST API — Overview & Architecture Specification

## 1. Executive Summary

The **Bloop REST API** (`/api/v1`) provides a strongly typed, deterministic, and versioned contract layer bridging the React/TypeScript frontend client with the FastAPI asynchronous backend engine. Designed for production scale and intermediate-level AI speech intelligence workflows, the API enforces rigid Pydantic validation, standardized response and error envelopes, dynamic provider abstraction, quantum subsystem decoupling, and strict user-scoped resource ownership.

---

## 2. Base Configuration & Environments

| Environment | Base URL | OpenAPI Specification | Interactive Docs (Swagger) | Alternative Docs (ReDoc) |
| :--- | :--- | :--- | :--- | :--- |
| **Development** | `http://localhost:8000/api/v1` | `/api/v1/openapi.json` | `/docs` | `/redoc` |
| **Test / Staging** | `http://testserver/api/v1` | `/api/v1/openapi.json` | `/docs` | `/redoc` |
| **Production** | `https://api.bloop.ai/api/v1` | Disabled (Configurable) | Disabled | Disabled |

All versioned endpoints are prefixed with `/api/v1`. The root endpoint (`GET /`) provides operational probe metadata without requiring authentication.

---

## 3. Standard JSON Envelopes

Every endpoint response returned by Bloop conforms strictly to a predictable JSON envelope structure.

### 3.1 Standard Success Envelope

```json
{
  "success": true,
  "data": {
    "id": 42,
    "text": "Bloop neural synthesis example.",
    "status": "completed"
  },
  "message": "Operation completed successfully.",
  "meta": null
}
```

### 3.2 Paginated Success Envelope

For collection endpoints, `data` contains a `PaginatedResponse` object, and the root envelope populates `meta` with standard `PaginationMeta`:

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 101,
        "text": "Speech item 1",
        "created_at": "2026-09-17T18:00:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20,
    "total_pages": 1,
    "has_next": false,
    "has_prev": false
  },
  "meta": {
    "page": 1,
    "page_size": 20,
    "total": 1,
    "total_pages": 1,
    "has_next": false,
    "has_prev": false
  },
  "message": "Speech generation history retrieved."
}
```

### 3.3 Standard Error Envelope

When any client or server error occurs, the API catches the exception and produces a uniform error envelope with HTTP status codes matching the problem domain:

```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "SpeechGeneration with identifier '999' not found",
    "details": {
      "resource": "SpeechGeneration",
      "identifier": "999"
    }
  }
}
```

---

## 4. Request Tracing & Security Headers

Every request processed by the Bloop middleware pipeline is assigned an idempotent or generated UUIDv4 `request_id`:

- **Client Header:** `X-Request-ID` (optional on inbound requests; sanitized if malicious characters are detected).
- **Response Header:** `X-Request-ID` is echoed on every response.
- **Timing Header:** `X-Process-Time` indicates latency in fractional milliseconds.
- **Security Headers:** `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Strict-Transport-Security` (in production).

---

## 5. Domain Modules & Route Summary

| Module | Route Prefix | Primary Purpose | Authentication |
| :--- | :--- | :--- | :--- |
| **Health** | `/` & `/health` | Liveness, readiness, probe checks | Public |
| **Auth** | `/api/v1/auth` | User registration, login, logout, token issuance | Public / Bearer |
| **Users** | `/api/v1/users` | Current user profile & synthesis preferences | Bearer Token |
| **Languages** | `/api/v1/languages` | Supported BCP-47 locales catalog | Public |
| **Voices** | `/api/v1/voices` | Dynamic voice discovery & query catalog | Public |
| **Speech (TTS)**| `/api/v1/tts` | Text synthesis, streaming audio, text analysis | Optional / Bearer |
| **History** | `/api/v1/history` | Generation audit trail, filtering, playback URLs | Bearer Token |
| **Favorites** | `/api/v1/favorites` | Generation bookmarking & curation library | Bearer Token |
| **Quantum** | `/api/v1/quantum` | QNN emotion analysis & circuit simulation | Public / Decoupled |

---

## 6. Dynamic Voice Registry & Zero-Secret Guarantee

1. **Dynamic Voice Architecture:** Bloop maintains a zero-hardcoding contract for third-party voice catalogs. No proprietary voice identifiers or vendor tokens are embedded into frontend assets or schema definitions.
2. **Provider Key Isolation:** All ElevenLabs and external provider credentials remain exclusively server-side. Frontend clients interact strictly with Bloop endpoints (`/api/v1/tts`, `/api/v1/voices`).
3. **Quantum Fault Isolation:** If the quantum subsystem is disabled (`QUANTUM_ENABLED=false`) or encounters an unrecoverable state, quantum endpoints yield an explicit 503 `QUANTUM_DISABLED` without breaking or degrading standard neural TTS synthesis.
