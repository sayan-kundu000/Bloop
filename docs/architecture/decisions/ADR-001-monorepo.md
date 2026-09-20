# ADR-001: Monorepo Architecture with Decoupled Frontend and Backend

## Status
**Accepted**

## Context
Bloop requires a full-stack architecture comprising a React Single Page Application (SPA), a Python FastAPI backend, database migrations, shared Postman/OpenAPI collections, and comprehensive documentation. 

We considered two architectural repository structures:
1. **Multi-repo structure:** Separate Git repositories for `bloop-frontend`, `bloop-backend`, and `bloop-docs`.
2. **Monorepo structure:** A single Git repository containing top-level `frontend/`, `backend/`, and `docs/` directories, sharing project-level configuration and documentation.

## Decision
We adopted a unified **Monorepo structure** with strictly decoupled root directories:
- `frontend/`: Independent React 19 + Vite + TypeScript application with its own `package.json`.
- `backend/`: Independent FastAPI + Python 3.11+ application with its own `requirements.txt` and virtual environment.
- `docs/`: Centralized technical documentation, PRS, architecture, and ADRs.

Neither the frontend nor backend depends on symlinks or shared cross-language build steps. Each service builds, tests, and deploys independently.

## Rationale
1. **Atomic Versioning & Traceability:** Allows changes spanning API contracts, frontend client types, and documentation to be reviewed, tracked, and committed atomically.
2. **Simplified Developer Experience:** Developers can clone a single repository and run both servers locally without managing multiple repository checkouts.
3. **Streamlined Cloud Deployments:** Render directly connects to the GitHub repository and targets the `backend` root directory. Vercel connects to the same repository and targets the `frontend` root directory.
4. **Intermediate-Level Complexity:** Avoids the operational overhead of enterprise monorepo tooling (Nx, Turborepo, Bazel) while maintaining complete logical separation.

## Consequences
### Positive
- Unified issue tracking, pull requests, and commit history.
- Zero duplication of specification documents and schemas.
- Straightforward CI/CD pipeline targeting specific subdirectories.

### Negative / Trade-offs
- Repository clone size includes all assets and documentation.
- CI workflows must use path-filtering to avoid triggering backend tests on frontend-only changes and vice versa.
