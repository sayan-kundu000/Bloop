# ADR-014: FastAPI Backend Foundation, Application Factory & Middleware Pipeline

## Status
**Accepted**

## Date
2026-09-17

## Context
As Bloop transitions from initial scaffolding into a multi-domain AI platform (supporting Text-to-Speech synthesis, dynamic voice registries, user profiles, history/favorites bookmarks, and quantum intelligence simulations), the backend requires a rock-solid, production-grade application architecture.

Key Challenges Addressed:
1. Monolithic vs. Factory Application Assembly: Monolithic global `app = FastAPI()` instances prevent clean test isolation and custom settings injection.
2. Cross-Cutting Observability: Distributed requests need correlation IDs, latency measurement, and security headers applied uniformly.
3. Exception Handling & Error Contracts: Route-level error handling causes disparate error JSON structures, risking accidental leakage of database tracebacks or internal credentials.
4. Resource Lifecycles: Database connection pools and HTTP clients need clean, non-blocking startup and deterministic teardown.

## Decision
1. **Adopt the Application Factory Pattern (`create_app()`)**: Implement `create_app(custom_settings: Optional[Settings] = None) -> FastAPI` in [`backend/app/factory.py`](file:///c:/Users/DELL/Downloads/Bloop/backend/app/factory.py), separating runtime assembly from ASGI execution in [`backend/app/main.py`](file:///c:/Users/DELL/Downloads/Bloop/backend/app/main.py).
2. **Establish an Ordered Middleware Pipeline**:
   - `CORSMiddleware`: Environment-restricted origins (no wildcard credentials in production).
   - `PayloadLimitMiddleware`: Drops oversized request bodies (>2MB) early to mitigate DoS.
   - `RequestIDMiddleware`: Validates or generates `X-Request-ID` correlation identifiers.
   - `SecurityHeadersMiddleware`: Injects defense-in-depth headers (`nosniff`, `DENY`, `strict-origin-when-cross-origin`).
   - `RequestTimingMiddleware`: Attaches `X-Response-Time` and outputs structured, secret-sanitized access logs.
3. **Standardize JSON Response Envelopes**:
   - Success: `{ "success": true, "data": ..., "message": ..., "meta": ... }`
   - Error: `{ "success": false, "error": { "code": ..., "message": ..., "details": ... } }`
4. **Implement Boundary Error Sanitization**: Intercept `SQLAlchemyError` and unhandled exceptions at the application boundary, logging tracebacks internally with `request_id` while returning sanitized error messages.
5. **Manage Async HTTP Client via Lifespan**: Initialize an application-scoped `httpx.AsyncClient` during startup and terminate connections during shutdown.
6. **Decouple Quantum and TTS**: Ensure the Quantum subsystem remains optional; its failure or absence never disrupts speech synthesis or general API routing.

## Consequences

### Positive
- High testability: Test suites instantiate isolated application instances with custom settings in milliseconds.
- Uniform client contract: Frontend interacts with predictable success and error envelopes across all endpoints.
- Total secret protection: Database credentials, JWT keys, and SQL queries are shielded from external clients.
- Clean resource lifecycle: Eliminates unclosed HTTP client sockets and orphaned database connection pools.

### Trade-offs
- Middleware overhead: Each request undergoes lightweight timing and header inspection (~0.1ms latency).
- Explicit error mapping: Developers must raise domain exceptions from the hierarchy rather than raw Python exceptions.
