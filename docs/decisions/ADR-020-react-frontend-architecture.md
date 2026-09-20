# ADR-020: React + TypeScript + Vite Frontend Architecture & UI Foundation

## Status
**Approved** (Implemented in Prompt 17)

---

## Context
Bloop requires an intermediate-level, production-oriented frontend web application serving two interconnected domains:
1. A core Text-to-Speech synthesis studio with history, favorites, audio playback, and account settings.
2. An isolated Quantum Intelligence laboratory containing style classification, emotion analysis, semantic similarity, interactive circuit design, and benchmarks.

Previous backend prompts established REST contracts, JWT authentication, database schemas, speech generation pipelines, and favorites/organization engines. The frontend must integrate with these backend foundations cleanly, maintaining strict provider isolation, zero secret leakage, dynamic voice consumption, and robust error recovery.

---

## Decision

### 1. Authoritative Frontend Stack
We standardize on:
- **UI Framework**: React 19
- **Language**: TypeScript (strict mode enabled)
- **Build Tool**: Vite 6
- **Styling**: Tailwind CSS (with glassmorphism and custom design tokens)
- **Routing**: React Router 7
- **Server State**: TanStack Query v5
- **Client UI State**: Zustand v5
- **Testing**: Vitest + React Testing Library (JSDOM)

Alternative frameworks (Next.js, Vue, Angular, Redux Toolkit, MobX, GraphQL) are rejected to minimize cognitive overhead and maintain direct compatibility with our FastAPI backend.

### 2. Strict State Management Boundary
- **Server State**: Handled exclusively by TanStack Query (`useQuery`, `useMutation`). Server data (profiles, preferences, speech generations, favorites, dynamic voices) is never mirrored into Zustand.
- **Client UI State**: Handled by Zustand stores (`authStore`, `workspaceStore`, `audioStore`) or local component state. Tracks ephemeral interface concerns (audio playback position, volume, draft textarea counts, mobile drawer visibility).

### 3. Dynamic Voice Invariant
The frontend strictly prohibits hardcoding actual or fake ElevenLabs voice IDs or catalogs. Voice catalogs are dynamically retrieved from `/api/v1/voices`. An empty catalog (`voices = []`) is a valid first-class state handled gracefully with empty-state messaging.

### 4. API Error Normalization & Session Handling
- All API exceptions are normalized into a typed `FrontendApiError` class capturing HTTP status, backend error codes, and human-friendly messages.
- HTTP 401 Unauthorized responses trigger automatic clearing of stale tokens in `localStorage` without entering infinite retry loops.

### 5. Route Protection & Accessibility
- `ProtectedRoute` guards authenticated routes, checking authentication and loading status to prevent flashing redirects.
- An accessible `NotFoundPage` captures unmatched routes.
- The `Navbar` provides a responsive mobile drawer menu with accessible ARIA attributes and keyboard Escape dismissal.
- `ErrorBoundary` protects the root tree, offering recovery buttons without exposing stack traces.

### 6. Deployment & Host Compatibility
- Single-page application routing is ensured via `vercel.json` rewrites.
- Only public variables prefixed with `VITE_` are consumed via `src/app/config.ts`. Backend secrets are audited and prohibited from client bundles.

---

## Consequences

### Positive
- **Maintainability**: Clear separation of concerns between UI primitives, layout shell, router, and feature modules.
- **Resilience**: Rendering errors and network failures are isolated and provide friendly user recovery flows.
- **Accessibility**: Semantic HTML, visible focus states, and ARIA attributes provide WCAG 2.1 AA compliance across desktop and mobile devices.
- **Zero Provider Coupling**: Frontend remains decoupled from third-party speech providers (ElevenLabs).

### Negative / Trade-offs
- TanStack Query cache invalidation requires intentional coordination on mutations.
- Dynamic voice loading requires UI to handle initial loading states before voice selection is available.
