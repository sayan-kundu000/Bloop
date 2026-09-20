# ADR-002: Selection of FastAPI for Backend REST API

## Status
**Accepted**

## Context
The Bloop backend must mediate commercial AI speech synthesis via ElevenLabs, execute in-process quantum simulations (Qiskit Aer, PennyLane), manage relational multi-tenant database records, stream audio files using HTTP 206 Partial Content, and serve interactive OpenAPI documentation.

We evaluated backend web frameworks across Python and Node.js ecosystems.

## Decision
Adopt **FastAPI (Python 3.11+)** running on **Uvicorn** ASGI server with **Pydantic v2** validation.

## Alternatives Considered
1. **Django / Django REST Framework:** Robust and batteries-included, but heavily opinionated, synchronous by default, burdened by monolithic architectural weight (ORM, templates, admin) that conflicts with our decoupled intermediate-level design.
2. **Flask:** Lightweight and familiar, but lacks native async I/O, requires numerous third-party plugins for OpenAPI, input validation, and JWT handling, leading to a fragmented "Frankenstein" architecture.
3. **Node.js (Express / NestJS):** Outstanding async I/O and TypeScript unification across full stack, but completely separates the web layer from the native Python scientific and quantum computing ecosystem (Qiskit, PennyLane, Scikit-Learn, NumPy), requiring expensive inter-process communication (gRPC or microservices).

## Consequences

### Positive
- **Unified Python Runtime:** Single runtime environment executes business logic, ElevenLabs HTTP requests, and Qiskit/PennyLane quantum circuits without inter-process overhead or RPC microservices.
- **Asynchronous Concurrency:** Native `async`/`await` allows non-blocking I/O during ElevenLabs HTTP requests and disk-based audio byte streaming.
- **Automated OpenAPI & Type Enforcement:** Pydantic v2 guarantees strict perimeter request validation and generates live Swagger UI (`/docs`) and ReDoc (`/redoc`) without manual schema synchronization.
- **High Performance:** Consistently benchmarks as one of the fastest Python frameworks, matching Go and Node.js performance for standard web I/O.

### Negative / Trade-offs
- **Async ORM Discipline:** Developers must understand async vs synchronous SQLAlchemy session semantics and avoid blocking event-loop execution during CPU-heavy tasks (mitigated by bounded quantum execution limits).
