# ADR-008: Monorepo Architecture with Decoupled Root Directories

## Status
**Accepted**

## Context
A full-stack application with frontend, backend, database migrations, Postman collections, and comprehensive documentation can be organized as multiple Git repositories or a single unified monorepo.

We considered the trade-offs between repository fragmentation and operational coordination.

## Decision
Adopt a **unified Monorepo structure** with decoupled, independent top-level directories:
- `frontend/`: Standalone React 19 + TypeScript + Vite project with independent `package.json`.
- `backend/`: Standalone FastAPI + Python project with independent `requirements.txt` and virtual environment.
- `docs/`: Centralized project documentation, PRS, architecture specifications, ADRs, and deployment guides.
- Root configuration: `.gitignore`, `.env.example`, `render.yaml`, `README.md`.

## Alternatives Considered
1. **Multi-Repo Structure (Separate `bloop-frontend`, `bloop-backend`, `bloop-docs`):** Increases overhead for versioning API contracts, synchronizing documentation, creating coordinated pull requests, and onboarding new developers who must clone and wire multiple repositories.
2. **Heavy Monorepo Tooling (Nx / Turborepo / Bazel):** Powerful for massive enterprise codebases with shared internal packages, but introduces complex build dependency graphs, specialized CLI tooling, and steep learning curves that contradict intermediate-level simplicity.

## Consequences

### Positive
- **Single Source of Truth:** Code, API contracts, TypeScript types, database migrations, and architectural documentation evolve together in atomic Git commits.
- **Seamless Developer Onboarding:** A new developer clones one repository and immediately has full access to the entire application ecosystem.
- **PaaS Multi-Root Compatibility:** Vercel natively points to the `frontend/` subfolder, while Render points to the `backend/` subfolder, enabling independent build and deploy lifecycles from a single GitHub repository.

### Negative / Trade-offs
- **CI Triggering:** Automated GitHub Actions must use path filters (`paths: ['backend/**']` or `paths: ['frontend/**']`) to avoid triggering unnecessary backend tests on frontend-only documentation or UI commits.
