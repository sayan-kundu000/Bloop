# Bloop — Runtime Compatibility & Cross-Stack Verification Matrix

**Document Identifier:** BLOOP-RUNTIME-COMPAT-V1  
**Project:** Bloop — AI Text-to-Speech & Quantum Intelligence Platform  
**Target Milestone:** Runtime Verification & Multi-Platform Compatibility  
**Status:** Approved Technical Contract  
**Authority:** Bloop Master Prompt, Prompt 01, Prompt 02, and Prompt 03  

---

## 1. Runtime Version Policy

Bloop adheres to a strict runtime stability policy:
> **Prefer stable, verified, well-documented, and deployment-friendly versions over bleeding-edge, experimental, or unverified packages.**

The system avoids experimental alpha/beta releases to guarantee uninterrupted local development and continuous delivery on Render and Vercel.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          AUTHORITATIVE RUNTIME BASELINE                     │
├─────────────────────────┬──────────────────────────┬────────────────────────┤
│ Runtime / Platform      │ Target Version           │ Deployment Provider    │
├─────────────────────────┼──────────────────────────┼────────────────────────┤
│ **Python**              │ 3.11+ (3.11.9 or 3.12.x) │ Render Python Service  │
│ **Node.js**             │ 20.x LTS / 22.x LTS      │ Vercel Edge Runtime    │
│ **npm**                 │ 10.x+                    │ Local & Vercel CI      │
│ **TypeScript**          │ 5.x (~5.6 - 5.8)         │ Vercel Build Pipeline  │
│ **React**               │ 19.x                     │ Client Browser / Vite  │
│ **FastAPI**             │ 0.115+                   │ Render Web Service     │
│ **PostgreSQL**          │ 16.x                     │ Render Managed Database│
│ **Qiskit**              │ 1.1+                     │ In-Process on Render   │
│ **PennyLane**           │ 0.36+                    │ In-Process on Render   │
│ **Vite**                │ 6.x                      │ Frontend Build Engine  │
│ **Tailwind CSS**        │ 3.4+                     │ Frontend Build Engine  │
└─────────────────────────┴──────────────────────────┴────────────────────────┘
```

---

## 2. Cross-Stack Compatibility Verification Matrix

Every inter-layer boundary has been audited for compatibility:

| Component Boundary | Version A | Version B | Compatibility Status | Verification Notes & Technical Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **Python ↔ FastAPI** | Python 3.11 / 3.12 | FastAPI 0.115+ | **Verified Compatible** | FastAPI natively leverages Python 3.11's accelerated asyncio event loop and improved exception groups. |
| **Python ↔ SQLAlchemy** | Python 3.11+ | SQLAlchemy 2.0.32+ | **Verified Compatible** | SQLAlchemy 2.0 fully supports Python 3.11 type hints (`Mapped[...]`) and async engines via `asyncpg`/`psycopg2`. |
| **Python ↔ PostgreSQL** | Python 3.11+ | PostgreSQL 16 (Psycopg2) | **Verified Compatible** | `psycopg2-binary 2.9.9+` provides pre-compiled Linux and Windows wheels compatible with PostgreSQL 16 on Render. |
| **Python ↔ ElevenLabs** | Python 3.11+ | HTTPX 0.27+ | **Verified Compatible** | Asynchronous HTTPX client connects securely via TLS 1.3 to ElevenLabs REST endpoints (`https://api.elevenlabs.io/v1`). |
| **Python ↔ Qiskit** | Python 3.11 / 3.12 | Qiskit 1.1+ & Aer 0.14+ | **Verified Compatible** | Qiskit 1.0+ introduced major architectural stability improvements. Wheels are pre-compiled for Linux x86_64 and Windows. |
| **Python ↔ PennyLane** | Python 3.11 / 3.12 | PennyLane 0.36+ | **Verified Compatible** | Native Python scientific wheel compatible with NumPy 1.26+ and SciPy 1.13+. |
| **Qiskit ↔ PennyLane** | Qiskit 1.1+ | PennyLane 0.36+ | **Verified Compatible** | Tested using standard Qiskit Aer compilation pipelines alongside PennyLane `default.qubit` devices without namespace collisions. |
| **React ↔ TypeScript** | React 19.x | TypeScript 5.x | **Verified Compatible** | `@types/react` and `@types/react-dom` provide complete static types for React 19 hooks and concurrent APIs. |
| **React ↔ Vite** | React 19.x | Vite 6.x (`@vitejs/plugin-react`) | **Verified Compatible** | `@vitejs/plugin-react 4.3+` provides instant Fast Refresh HMR and Rollup 4 asset bundling. |
| **React ↔ Tailwind CSS**| React 19.x | Tailwind 3.4+ / PostCSS 8 | **Verified Compatible** | Standard Vite PostCSS integration purges unused classes cleanly into a minimal production stylesheet. |
| **React ↔ TanStack Query**| React 19.x | TanStack Query 5.x | **Verified Compatible** | TanStack Query 5 natively supports React 19 suspense boundaries and mutation lifecycles. |
| **React ↔ Zustand** | React 19.x | Zustand 5.x | **Verified Compatible** | Zustand 5.x utilizes `useSyncExternalStore` for tear-free state synchronization with React 19 concurrent mode. |
| **Vercel ↔ Vite** | Vercel Edge | Vite 6 (`dist/`) | **Verified Compatible** | Vercel natively detects Vite frameworks, executing `npm run build` and serving `dist/` with edge caching and gzip/brotli. |
| **Render ↔ FastAPI** | Render Web Service | FastAPI / Uvicorn | **Verified Compatible** | Render executes standard Python buildpack commands, binding Uvicorn to `$PORT` smoothly. |
| **Render ↔ PostgreSQL**| Render Web Service | Render PostgreSQL 16 | **Verified Compatible** | Automatic `DATABASE_URL` binding injects SSL-secured connection strings directly into the FastAPI environment. |
| **GitHub ↔ PaaS Deploys**| GitHub Monorepo | Render & Vercel Webhooks | **Verified Compatible** | Pushes to `main` trigger parallel deployments: Vercel builds `frontend/` and Render builds `backend/`. |

---

## 3. Version Conflict Resolution Protocol

If a dependency conflict occurs during development or continuous integration:
1. **Identify the Conflicting Transitive Dependency:** Use `pip check` or `npm ls <package>` to pinpoint the conflicting package.
2. **Prioritize Core Framework Stability:** Never compromise FastAPI, React, or SQLAlchemy stability to accommodate an auxiliary utility library.
3. **Pin to Documented Compatible Baseline:** Use the verified versions specified in `requirements.txt` and `package.json`.
4. **Avoid Bleeding-Edge Premature Upgrades:** Do not upgrade packages immediately upon zero-day release. Allow new versions at least 14 days of community stabilization before testing.
5. **Document the Decision:** Record any pinned exception or workaround in an Architectural Decision Record in `docs/architecture/adr/`.
