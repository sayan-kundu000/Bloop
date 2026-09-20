# Bloop Architecture — Canonical Repository Structure

## 1. Overview & Monorepo Strategy

The **Bloop AI Text-to-Speech & Quantum Intelligence Platform** is structured as a unified, high-cohesion, low-coupling **single GitHub monorepo**:

```text
GitHub
   ↓
Bloop Monorepo
   ├── Frontend       (React 18 + TypeScript + Vite + Tailwind + TanStack Query + Zustand)
   ├── Backend        (FastAPI + Pydantic v2 + SQLAlchemy 2.x + Qiskit + PennyLane)
   ├── Documentation  (ADRs, System Design, Data Flow, Coding Standards)
   ├── Tests          (Unit, Integration, API, Providers, Quantum, E2E, Smoke)
   ├── Configuration  (Environment variable schemas, Linters, EditorConfig)
   └── Deployment     (Vercel SPA + Render Web Service + Render PostgreSQL)
```

The monorepo is the single source of truth. No separate repositories exist for frontend/backend or quantum subsystems.

---

## 2. Complete Monorepo Directory Tree

```text
bloop/
│
├── .github/
│   └── workflows/
│       ├── ci.yml                    # Automated lint & test pipeline for Frontend & Backend
│       └── audit.yml                 # Dependency CVE vulnerability audit
│
├── .editorconfig                     # Multi-editor whitespace and charset consistency
├── .gitignore                        # Strict exclusion of virtualenvs, node_modules, and secrets
│
├── frontend/                         # Client-Side Application Boundary
│   ├── public/                       # Static public assets, favicons, manifests
│   ├── src/
│   │   ├── app/                      # App composition: router, providers, config
│   │   │   ├── App.tsx
│   │   │   ├── router.tsx
│   │   │   ├── providers.tsx
│   │   │   ├── config.ts
│   │   │   └── index.ts
│   │   ├── assets/                   # SVG icons, character avatars, typography
│   │   ├── components/               # Reusable UI component library
│   │   │   ├── ui/                   # Reusable visual primitives (Button, Input, Card, Badge)
│   │   │   ├── common/               # Shell components (Navbar, Footer, StateViews)
│   │   │   ├── forms/                # FormField, Label, InputFeedback
│   │   │   └── feedback/             # AlertBanner, Toast, StatusBadge
│   │   ├── features/                 # Modular feature domains (components, hooks, types)
│   │   │   ├── auth/                 # Login, register, token handling
│   │   │   ├── user/                 # Profile management, preferences
│   │   │   ├── languages/            # Language catalog & filtering
│   │   │   ├── voices/               # Dynamic voice catalog & previews
│   │   │   ├── tts/                  # Speech synthesis workspace & parameters
│   │   │   ├── audio/                # Audio player, waveforms, download
│   │   │   ├── history/              # Generation logs & pagination
│   │   │   ├── favorites/            # Starred voices & audio bookmarks
│   │   │   └── quantum/              # Quantum circuit visualization & benchmarks
│   │   ├── hooks/                    # General custom React hooks (e.g., useDebounce)
│   │   ├── layouts/                  # Structural page shells (AppLayout, AuthLayout)
│   │   ├── lib/                      # Client infrastructure
│   │   │   ├── api/                  # Typed HTTP client & error normalizer
│   │   │   ├── query/                # TanStack Query client & queryKeys catalog
│   │   │   ├── validation/           # Client-side input validation rules
│   │   │   └── utilities/            # Formatters and converters
│   │   ├── pages/                    # Route-level page composition
│   │   ├── services/                 # Cross-feature application services
│   │   ├── stores/                   # Zustand stores for ephemeral UI state
│   │   ├── types/                    # Shared TypeScript interfaces
│   │   ├── utils/                    # Text statistics & audio helpers
│   │   ├── styles/                   # Custom CSS animations & design tokens
│   │   ├── App.tsx                   # Top-level application entry
│   │   └── main.tsx                  # React 18 DOM root mount point
│   ├── tests/                        # Vitest unit and integration suites
│   │   ├── components/               # UI primitive tests
│   │   ├── features/                 # Domain logic and queryKey tests
│   │   ├── hooks/                    # React hook behavior tests
│   │   ├── setup.ts                  # Test harness setup
│   │   └── validation.test.ts        # Client boundary validation tests
│   ├── .env.example                  # Frontend environment template
│   ├── index.html                    # Single Page Application HTML shell
│   ├── package.json                  # Dependencies & build scripts
│   ├── tsconfig.json                 # TypeScript strict compiler options
│   ├── vite.config.ts                # Vite build & bundle configuration
│   └── README.md                     # Frontend developer documentation
│
├── backend/                          # Server-Side Application Boundary
│   ├── app/
│   │   ├── api/                      # Routing & dependency injection
│   │   │   ├── dependencies/         # Reusable route dependencies (auth, db)
│   │   │   ├── routes/               # Clean route modules by domain
│   │   │   └── v1/                   # Versioned router & endpoints
│   │   ├── core/                     # Application infrastructure
│   │   │   ├── config.py             # Pydantic BaseSettings environment config
│   │   │   ├── security.py           # Password hashing & JWT issuance
│   │   │   ├── logging.py            # Structured JSON / colored logging
│   │   │   ├── exceptions.py         # Standardized domain error classes
│   │   │   └── rate_limit.py         # Request rate limiter
│   │   ├── db/                       # Database engine & session layer
│   │   │   ├── base.py               # Declarative Base & model discovery
│   │   │   ├── session.py            # Engine & SessionLocal maker
│   │   │   └── dependencies.py       # Request-scoped get_db dependency
│   │   ├── models/                   # SQLAlchemy 2.x declarative models
│   │   │   ├── user.py
│   │   │   ├── preference.py
│   │   │   ├── language.py
│   │   │   ├── voice.py
│   │   │   ├── generation.py
│   │   │   ├── favorite.py
│   │   │   └── quantum_experiment.py
│   │   ├── schemas/                  # Pydantic v2 request/response schemas
│   │   │   ├── common.py
│   │   │   ├── user.py
│   │   │   ├── tts.py
│   │   │   ├── voice.py
│   │   │   └── quantum.py
│   │   ├── repositories/             # Database persistence operations
│   │   │   ├── user_repository.py
│   │   │   ├── generation_repository.py
│   │   │   ├── favorite_repository.py
│   │   │   └── quantum_repository.py
│   │   ├── services/                 # Domain business workflow coordination
│   │   │   ├── auth_service.py
│   │   │   ├── voice_service.py
│   │   │   ├── tts_service.py
│   │   │   └── quantum_service.py
│   │   ├── providers/                # External adapters & integrations
│   │   │   ├── tts/                  # TTS provider subsystem
│   │   │   │   ├── base.py           # Abstract TTSProvider contract
│   │   │   │   ├── elevenlabs.py     # ElevenLabs API adapter
│   │   │   │   ├── simulation.py     # Neural synthesis fallback provider
│   │   │   │   └── types.py          # Provider options & result types
│   │   │   ├── elevenlabs_provider.py
│   │   │   └── simulation.py
│   │   ├── quantum/                  # Isolated Quantum Intelligence Subsystem
│   │   │   ├── circuits/             # Qiskit circuit constructions
│   │   │   ├── algorithms/           # VQC classification & emotion QNNs
│   │   │   ├── models/               # Quantum state vectors & parameters
│   │   │   ├── services/             # High-level quantum orchestration
│   │   │   ├── simulators/           # AerSimulator & PennyLane device configs
│   │   │   ├── benchmarks/           # Empirical quantum vs classical benchmarks
│   │   │   └── utilities/            # Angle encoding & phase estimators
│   │   └── main.py                   # FastAPI app factory, middleware, CORS
│   ├── alembic/                      # Database migration environment
│   │   ├── versions/                 # Versioned migration scripts
│   │   └── env.py                    # Migration execution environment
│   ├── tests/                        # Categorized Pytest suites
│   │   ├── unit/                     # Business logic and input validation tests
│   │   ├── integration/              # Database persistence & transaction tests
│   │   ├── api/                      # Route response tests
│   │   ├── repositories/             # Repository layer persistence tests
│   │   ├── providers/                # SimulationTTSProvider & ElevenLabs tests
│   │   ├── quantum/                  # Qiskit circuit & PennyLane QNN tests
│   │   └── fixtures/                 # Backend sample test fixtures
│   ├── .env.example                  # Backend secrets template
│   ├── alembic.ini                   # Alembic database migration config
│   ├── requirements.txt              # Production Python dependencies
│   ├── requirements-dev.txt          # Linting, testing, and formatting tools
│   ├── pytest.ini                    # Pytest configuration & asyncio mode
│   └── README.md                     # Backend architecture & developer guide
│
├── docs/                             # Engineering & Product Documentation
│   ├── architecture/                 # System architecture, ADRs, and diagrams
│   │   ├── adr/                      # Architectural Decision Records (ADR-001 - ADR-011)
│   │   ├── diagrams/                 # Mermaid system architecture diagrams
│   │   └── decisions/                # Technology evaluation records
│   ├── development/                  # Local setup & coding conventions
│   ├── deployment/                   # Render + Vercel deployment playbooks
│   ├── api/                          # OpenAPI documentation & contract details
│   ├── database/                     # Schema design & relational data dictionary
│   ├── quantum/                      # Quantum feature encoding & QNN math notes
│   ├── product/                      # Product Requirements & scope specs
│   └── standards/                    # Code standards, Git conventions & Antigravity IDE guide
│
├── tests/                            # Cross-Cutting & Deployment Test Suites
│   ├── e2e/                          # Cross-boundary API end-to-end test scenarios
│   ├── smoke/                        # Fast deployment verification & health probes
│   ├── fixtures/                     # Test JSON payloads & sample audio inputs
│   └── README.md                     # Cross-cutting test runner instructions
│
├── scripts/                          # Monorepo Automation Scripts
│   ├── development/                  # dev.ps1 & dev.sh local multi-service launch
│   ├── database/                     # migrate.ps1 & migrate.sh Alembic helpers
│   ├── deployment/                   # check-health.ps1 & check-health.sh live probes
│   └── README.md                     # Monorepo automation reference
│
├── README.md                         # Master repository README
└── LICENSE                           # Repository open license
```

---

## 3. Directory Responsibilities Matrix

| Directory | Layer | Allowed Dependencies | Prohibited Dependencies |
| :--- | :--- | :--- | :--- |
| `frontend/src/app` | Root Composition | `pages`, `layouts`, `lib`, `components` | Feature-specific business rules |
| `frontend/src/features/<feat>` | Domain Feature | `components/ui`, `lib/api`, `stores` | Other feature internal files |
| `frontend/src/components/ui` | Visual Primitives | None (Vanilla React/Tailwind) | Features, Pages, API Clients |
| `frontend/src/stores` | UI State | None | Server response caches |
| `backend/app/api/routes` | HTTP Perimeter | `services`, `schemas`, `dependencies` | Direct DB queries, Provider APIs |
| `backend/app/services` | Business Logic | `repositories`, `providers`, `schemas` | FastAPI request/response objects |
| `backend/app/repositories`| Persistence | `models`, `db/session` | HTTP routes, external APIs |
| `backend/app/providers` | External Adapters | `providers/tts/types` | Frontend, database models |
| `backend/app/quantum` | Intelligence Engine| `qiskit`, `pennylane`, `numpy` | FastAPI routes, database models |
