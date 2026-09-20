# Bloop — Antigravity IDE Execution & Prompt Chaining Guide

**Document Identifier:** BLOOP-ANTIGRAVITY-V1  
**Authority:** Bloop Master Prompt & Prompt 04  

---

## 1. Role of Antigravity IDE

Antigravity operates as the master AI implementation pair-programmer and software architect for Bloop. To ensure reliable, non-regressive, incremental implementation across staged prompts, the agent follows strict operational rules:

```
INSPECT ──► READ ARCHITECTURE ──► MAP REQUIREMENTS ──► DESIGN BOUNDARIES ──► IMPLEMENT ──► TEST ──► VERIFY ──► REPORT
```

---

## 2. Invariants for Antigravity Execution

1. **The Decoupled Architecture Invariant:** Never couple core Text-to-Speech synthesis to quantum execution. Quantum failures must never crash TTS endpoints.
2. **The Zero Fabricated Voices Invariant:** Never inject fake voice IDs, mock voice names, or hardcoded vendor voice catalogues into production source code. Voices are ingested dynamically at runtime.
3. **The Secret Isolation Invariant:** Never write `ELEVENLABS_API_KEY`, database connection passwords, or JWT secrets into frontend code, client bundles, or committed files.
4. **The Dependency Minimalism Invariant:** Do not add microservices, Celery, Kafka, Redis, or Kubernetes. Bloop deploys cleanly as one FastAPI web service on Render, one PostgreSQL database, and one React SPA on Vercel.
5. **No Regressions:** When implementing new features, always verify that previous tests (`pytest`, `npm test`) continue to pass.

---

## 3. Staged Prompt Execution Sequence

Bloop is constructed through a 16-stage disciplined engineering prompt series:

| Prompt | Stage Name | Status | Key Deliverables |
| :--- | :--- | :--- | :--- |
| **Prompt 01** | Product Requirements, Scope & MVP Contract | **Complete** | `product-requirements.md`, `scope.md`, `mvp-contract.md`, `acceptance-criteria.md` |
| **Prompt 02** | Full-Stack Architecture, Data Flow & Boundaries | **Complete** | `system-architecture.md`, `tts-data-flow.md`, `quantum-architecture.md`, ADRs |
| **Prompt 03** | Elite Tech Stack, Dependencies & Deployment-First | **Complete** | `technology-stack.md`, `dependency-strategy.md`, `runtime-compatibility.md`, 10 ADRs |
| **Prompt 04** | GitHub Monorepo, Repository Standards & Foundation | **Complete** | Scaffolding, CI workflows (`ci.yml`, `audit.yml`), automation scripts, test suites |
| **Prompt 05** | Complete Directory Structure, Code Organization & Conventions | **Complete** | `repository-structure.md`, `code-organization.md`, `module-boundaries.md`, `dependency-rules.md`, `coding-conventions.md`, `project-navigation.md`, ADR-011, Diagrams |
| **Prompt 06** | Configuration, Environment Management & Runtime Foundation | Upcoming | Application settings, runtime config, environment management, database fallback |
| **Prompt 07** | Text Input Engine, Live Counters & Validation | Upcoming | Character/word counters, duration estimator, length boundary guards |
| **Prompt 08** | Dynamic Voice Architecture & Multilingual Locales | Upcoming | Dynamic voice registry, language selector, voice ingestion modal |
| **Prompt 09** | ElevenLabs Provider & Offline Simulation Fallback | Upcoming | `BaseTTSProvider`, `ElevenLabsProvider`, `SimulationTTSProvider` |
| **Prompt 10** | Audio Storage & HTTP 206 Streaming Engine | Upcoming | Chunked MP3 streaming, byte-range scrubbing, download endpoint |
| **Prompt 11** | Authentication, User Isolation & Security Perimeter | Upcoming | Bcrypt hashing, JWT authorization, multi-tenant query scoping |
| **Prompt 12** | React 19 Frontend Studio & Persistent Audio Player | Upcoming | Full frontend workspace UI, audio scrubber, glassmorphic layout |
| **Prompt 13** | Speech History, Multi-Filter Search & Bookmarks | Upcoming | Paginated history table, multi-parametric filtering, favorites |
| **Prompt 14** | Quantum Intelligence Laboratory & 5 Modular Engines | Upcoming | Qiskit VQC, PennyLane Affective QNN, Semantic Kernel, Circuit Lab |
| **Prompt 15** | End-to-End Testing, Smoke Probes & Quality Assurance| Upcoming | Full automated test coverage, mock suites, integration verification |
| **Prompt 16** | Cloud Deployment on Render & Vercel | Upcoming | Production PaaS deployment, database migrations, DNS/SSL verification |
