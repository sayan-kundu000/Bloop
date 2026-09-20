# ADR-011: Complete Code Organization, Layered Boundaries, and Module Responsibilities

## Status
**Accepted**

## Context
As Bloop progresses from initial setup to incremental multi-feature implementation, having ambiguous code placement leads to duplicated logic, bloated files, circular imports, and confusion for developers and AI coding assistants. We need an authoritative architectural blueprint defining exact code placement, layer invariants, and directory responsibilities.

## Decision
Establish the canonical Bloop code organization framework with strict layer invariants:
1. **Single Monorepo with Autonomous Root Boundaries:** `frontend/`, `backend/`, `tests/`, `docs/`, `scripts/`, `.github/`.
2. **Feature-Oriented Frontend Layout:** Reusable UI primitives isolated in `components/ui/`; domain logic contained in `features/<domain>/` with dedicated components, hooks, and types; pages acting solely as high-level feature compositors.
3. **Clean Architecture Backend Layering:** Strict unidirectional execution:
   `API Routes → Services → Repositories / Providers / Quantum → Persistence / External APIs`.
4. **Isolated Quantum Computing Boundary:** Quantum algorithms (`backend/app/quantum/`) are strictly additive. They cannot import web routes or SQL database models, and their failure can never block core speech synthesis.
5. **Decoupled Provider Architecture:** Vendor integrations (ElevenLabs) and neural fallbacks (`SimulationTTSProvider`) are isolated behind the abstract `TTSProvider` contract.
6. **No Shared Root Build Tools:** Avoid enterprise monorepo orchestrators (Nx, Turborepo) in favor of standard NPM and Python package ecosystems.

## Alternatives Considered
1. **Flat / Giant Module Architecture:** Placing all routes in one `api.py` and all business logic in `main.py`. Rejected due to unmaintainability and merge conflicts.
2. **Microservices / Multi-Repository:** Splitting Quantum, TTS, and Auth into microservices. Rejected because intermediate developers need straightforward local setups without Kubernetes or distributed tracing.
3. **Duplicating Server State in Zustand:** Caching API responses in global Zustand stores. Rejected in favor of TanStack Query for server state and Zustand exclusively for ephemeral client UI state.

## Consequences

### Positive
- **Deterministic Placement:** Every new feature has an unmistakable target directory.
- **Testability:** Every layer (route, service, repository, provider, quantum engine) can be tested in isolation.
- **Zero Secrets / No Hardcoded Data:** Security perimeter remains intact; voice IDs and API keys are strictly runtime-configured.
- **Deployment-Friendly:** Frontend builds to static assets on Vercel; backend runs as a single FastAPI process on Render.

### Trade-offs
- Requires discipline to maintain layer boundaries and avoid quick shortcuts (e.g. executing SQL queries inside route functions).
