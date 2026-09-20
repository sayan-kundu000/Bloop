# ADR-012: Environment Configuration, Secrets Management & Development/Production Profiles

## Status
**Accepted**

## Context
Bloop is an AI Text-to-Speech & Quantum Intelligence platform designed to run consistently across local developer workstations, automated CI/CD test runners, Render managed cloud hosting (FastAPI backend + PostgreSQL 16), and Vercel Edge CDN (React 19 frontend). 

Prior to this architecture decision, environment variables and configuration settings were at risk of becoming fragmented across multiple modules, with inconsistent naming conventions (`ENVIRONMENT` vs `APP_ENV`, `SECRET_KEY` vs `JWT_SECRET_KEY`), potential secret exposure to client bundles, lack of automated validation during deployment startup, and risk of automated tests accidentally connecting to production databases.

## Problem
1. **Source Code Modifications Across Environments:** Without a strict Twelve-Factor externalized configuration model, developers might resort to changing constants or code flags between local development and cloud deployment.
2. **Secret Leakage Risks:** Frontend SPA bundles compile all bundled code into public client assets. Any private API keys (`ELEVENLABS_API_KEY`, `JWT_SECRET_KEY`, `DATABASE_URL`) inadvertently prefixed or referenced in frontend code become publicly visible in the browser.
3. **Silent Misconfigurations in Production:** If an application silently boots in production with `DEBUG=True`, weak default secret keys, or wildcard CORS origins (`*`), severe security vulnerabilities are introduced.
4. **Test Destructiveness:** If test environments accidentally inherit a production database connection string, test fixture cleanup routines (`drop_all`) could irreversibly destroy production data.

## Decision
Establish a centralized, typed, environment-aware, and secure configuration architecture governed by the foundational principle:
> **Same codebase, different configuration — never different source code for different environments.**

### 1. Environment Profiles
Establish exactly three canonical runtime profiles:
- **`development`**: Optimized for local iteration, rapid debugging, readable logs, local SQLite/PostgreSQL, and optional external services (SimulationTTS fallback).
- **`test`**: Optimized for deterministic execution, isolated test database (`test_bloop.db`), mocked external providers, and fail-fast protection against production database URLs.
- **`production`**: Optimized for security, reliability, controlled logging, strict CORS policies, enforced persistent PostgreSQL, and high-entropy secrets.

### 2. Configuration Architecture & Immutability
- **Backend (`backend/app/core/config.py`)**: Centralize all settings in a typed `pydantic-settings` model (`Settings`). All backend services must consume settings via dependency injection or the cached singleton `settings = get_settings()`. Arbitrary `os.getenv()` calls across business services are strictly forbidden.
- **Frontend (`frontend/src/app/config.ts`)**: Centralize all public client settings in a frozen, immutable `AppConfig` object. Components must never access `import.meta.env` directly.
- **Secret Masking**: Implement custom `__repr__` and `__str__` in `Settings` to scrub passwords, JWT secrets, and API keys. Attach a `SecretMaskingFilter` to the root logging pipeline.

### 3. Secret Classification Contract
Classify all platform configuration into three explicit tiers:
1. **Public**: Safe for browser consumption. Exclusively prefixed with `VITE_` (e.g. `VITE_API_BASE_URL`).
2. **Private**: Backend-only operational configuration that is non-sensitive (e.g. `APP_ENV`, `PORT`, `LOG_LEVEL`, `CORS_ORIGINS`, `AUDIO_STORAGE_PATH`).
3. **Secret**: Highly sensitive credentials that must never be exposed, committed, or logged (e.g. `DATABASE_URL`, `JWT_SECRET_KEY`, `ELEVENLABS_API_KEY`).

### 4. Frontend / Backend Boundary
- **Frontend**: Only receives `VITE_API_BASE_URL`. Performs runtime environment auditing to ensure no private keys or secrets are bundled.
- **Backend**: Ingests private settings and secrets via Render environment variables or local git-ignored `.env` files. Communicates with ElevenLabs and PostgreSQL strictly server-side.

### 5. Automated Startup Safeguards
Implement fail-fast validation in `Settings`:
- If `APP_ENV == "production"`:
  - Startup fails if `APP_DEBUG == True`.
  - Startup fails if `JWT_SECRET_KEY` is empty, less than 32 characters, or matches default dev placeholders.
  - Startup fails if `DATABASE_URL` is empty or points to SQLite.
  - Startup fails if `CORS_ORIGINS` contains wildcard `*`.
- If `APP_ENV == "test"`:
  - Execution fails immediately if `DATABASE_URL` contains production domain indicators (`render.com`, `dpg-`, `prod`).

### 6. Deployment Strategy
- **Render Backend**: All secrets (`DATABASE_URL`, `JWT_SECRET_KEY`, `ELEVENLABS_API_KEY`, `CORS_ORIGINS`) are injected via Render Dashboard Environment Variables. No secrets are stored in `render.yaml` or repository files.
- **Vercel Frontend**: Public endpoint `VITE_API_BASE_URL` is configured in Vercel Project Settings for Preview and Production environments.

## Alternatives Considered
1. **HashiCorp Vault / AWS Secrets Manager / Kubernetes Secrets:** Rejected as inappropriate enterprise overhead for the current intermediate-level architecture. Render and Vercel native environment secret management provides robust encryption-at-rest and least-privilege access without additional infrastructure.
2. **Scattered `os.getenv()` Calls:** Rejected due to lack of type safety, missing defaults, zero validation at startup, and difficult test mocking.
3. **Direct Frontend ElevenLabs API Calls:** Rejected because distributing vendor API keys to browser bundles exposes billing and quota to reverse engineering.

## Consequences

### Positive
- **Deterministic Deployments:** The exact same Docker container or Git commit runs seamlessly in local dev, test runners, and production.
- **Fail-Fast Security:** Any misconfiguration in production is rejected at application boot before receiving traffic.
- **Zero Accidental Secret Commits:** Strict `.gitignore` rules and automated secret masking protect credentials from repository leaks and log files.
- **Complete Test Isolation:** Automated tests are mathematically blocked from executing against production databases.

### Trade-offs
- Setting up a new developer machine requires copying `.env.example` to `.env` and generating a local JWT secret.
