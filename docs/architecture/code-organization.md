# Bloop Code Organization — "Where Does Every Piece of Code Belong?"

## 1. The Core Organization Principle

Every piece of code in Bloop follows this strict resolution chain:

```text
Feature / Requirement
    ↓
Correct Layer
    ↓
Correct Directory
    ↓
Correct Module
    ↓
Single Clear Responsibility
```

---

## 2. Definitive Code Placement Matrix

Use this lookup matrix before creating or modifying any file:

| Code / Requirement Type | Target Directory | Canonical Example File | File Responsibility |
| :--- | :--- | :--- | :--- |
| **Top-Level Root App** | `frontend/src/app/` | `App.tsx`, `router.tsx`, `providers.tsx` | Assembles top-level providers, router shell, and global layout. |
| **UI Primitive (Atoms)** | `frontend/src/components/ui/` | `Button.tsx`, `Input.tsx`, `Card.tsx` | Pure, stateless, reusable presentation components styled with Tailwind. |
| **Shell UI (Molecules)** | `frontend/src/components/common/` | `Navbar.tsx`, `Footer.tsx`, `StateViews.tsx` | Application-wide navigation bars, empty states, error cards, loaders. |
| **Form Controls** | `frontend/src/components/forms/` | `FormField.tsx`, `InputFeedback.tsx` | Labels, error states, and helper text wrappers. |
| **Feedback UI** | `frontend/src/components/feedback/` | `AlertBanner.tsx`, `Toast.tsx` | Global status banners and user notifications. |
| **Domain Feature Logic** | `frontend/src/features/<feature>/` | `features/tts/index.ts`, `components/` | Domain-isolated components, hooks, and types for a specific feature. |
| **General React Hooks** | `frontend/src/hooks/` | `useDebounce.ts`, `useAudioPlayer.ts` | Cross-cutting custom hooks not bound to a single feature domain. |
| **Route-Level Pages** | `frontend/src/pages/` | `WorkspacePage.tsx`, `DashboardPage.tsx` | Composes feature modules into complete page views. No direct DB/API code. |
| **Page Layouts** | `frontend/src/layouts/` | `AppLayout.tsx`, `AuthLayout.tsx` | Structural frames (sidebar, header, content viewport). |
| **Client HTTP Client** | `frontend/src/lib/api/` | `client.ts` | Centralized fetch wrapper, token injection, error normalization. |
| **Server State (Queries)**| `frontend/src/lib/query/` | `index.ts`, `queryKeys` | TanStack Query client configuration and standardized query key factory. |
| **Ephemeral UI State** | `frontend/src/stores/` | `workspaceStore.ts`, `audioStore.ts` | Zustand stores for active audio playback, editor text, and UI toggles. |
| **Client Validation** | `frontend/src/utils/` | `validation.ts`, `formatters.ts` | Fast UX input validation (empty text, speed bounds, character counters). |
| **HTTP Route Perimeter**| `backend/app/api/routes/` | `tts.py`, `voices.py`, `health.py` | Receives HTTP requests, validates schemas, invokes services, returns JSON. |
| **API Dependencies** | `backend/app/api/dependencies/` | `auth.py`, `db.py`, `deps.py` | FastAPI request-scoped dependencies (current user, DB session). |
| **System Configuration** | `backend/app/core/` | `config.py`, `security.py` | Pydantic BaseSettings, password hashing, JWT token handling. |
| **System Exceptions** | `backend/app/core/exceptions.py` | `exceptions.py` | Standardized domain exception classes mapped to HTTP error codes. |
| **Rate Limiting** | `backend/app/core/rate_limit.py` | `rate_limit.py` | Sliding window rate limit validator per IP or user. |
| **Database Engine / Base**| `backend/app/db/` | `session.py`, `base.py` | SQLAlchemy engine, session maker, and model auto-discovery registry. |
| **Database ORM Models** | `backend/app/models/` | `user.py`, `voice.py`, `generation.py` | SQLAlchemy declarative database table representations. |
| **API Pydantic Schemas** | `backend/app/schemas/` | `tts.py`, `voice.py`, `quantum.py` | Request/response data validation contracts and serialization. |
| **Persistence Repos** | `backend/app/repositories/` | `user_repository.py`, `voice_repo.py` | Raw SQLAlchemy CRUD, queries, filters, and pagination. |
| **Business Workflows** | `backend/app/services/` | `tts_service.py`, `voice_service.py` | Orchestrates repositories, providers, and business validation rules. |
| **TTS Provider Adapters**| `backend/app/providers/tts/` | `elevenlabs.py`, `simulation.py` | Concrete implementations of the abstract `TTSProvider` contract. |
| **Quantum Algorithms** | `backend/app/quantum/` | `algorithms/`, `circuits/`, `models/` | Qiskit circuits, PennyLane QNNs, variational classifiers, benchmarks. |
| **Database Migrations** | `backend/alembic/versions/` | `001_initial_schema.py` | Alembic revision migration files. |
| **Integration Tests** | `backend/tests/integration/` | `test_db_persistence.py` | Multi-step database transaction and session tests. |
| **Unit Tests** | `backend/tests/unit/` | `test_text_validation.py` | Pure logic validation and boundary condition tests. |
| **API Route Tests** | `backend/tests/api/` | `test_health_routes.py` | FastAPI testclient HTTP request/response tests. |
| **Smoke & E2E Tests** | `tests/smoke/`, `tests/e2e/` | `test_smoke.py`, `test_api_e2e.py` | Deployment health checks and cross-boundary end-to-end user workflows. |
| **Automation Scripts** | `scripts/development/` | `dev.ps1`, `dev.sh` | Local multi-service startup, Alembic migrations, health probes. |

---

## 3. Cohesion Over Fragmentation Rule

- **Do NOT** split every 2-line helper function into its own isolated file.
- **Do NOT** bundle unrelated responsibilities (e.g. database queries + ElevenLabs HTTP calls) into one giant file.
- When adding a feature:
  1. Check if an existing domain module already owns the responsibility.
  2. If yes, extend that module cleanly.
  3. If no, create a new focused module inside the appropriate layer directory.
