# Bloop — Intermediate-Level MVP Contract

**Document Identifier:** BLOOP-MVP-CONTRACT-V1  
**Project:** Bloop — AI Text-to-Speech & Quantum Intelligence Platform  
**Target Milestone:** Intermediate-Level MVP  
**Status:** Binding Engineering Contract  
**Authority:** Bloop Master Prompt & Prompt 01

---

## 1. The MVP Philosophy: Complete Intermediate Software

In the Bloop development lifecycle, **MVP does NOT mean a minimal, throwaway prototype**.

Bloop's MVP is an **Intermediate-Level, Production-Ready Full-Stack AI Platform**. It delivers real utility, robust security, comprehensive data persistence, modern aesthetics, automated test coverage, and cloud deployment.

### The Bloop Core Formula:

$$\text{Bloop MVP} = \begin{aligned}
& \text{Authentication} + \text{TTS Pipeline} + \text{ElevenLabs} + \text{PostgreSQL} \\
& + \text{History \& Favorites} + \text{Search \& Filtering} + \text{Responsive UI} \\
& + \text{Quantum Intelligence Lab} + \text{Automated Tests} + \text{Cloud Deployment}
\end{aligned}$$

---

## 2. Mandatory Must-Have Features (Section 22)

Every feature in the following matrix is a non-negotiable requirement of the Intermediate MVP:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       MANDATORY MVP FEATURE STACK                           │
├───────────────────────┬─────────────────────────────┬───────────────────────┤
│ 1. Core TTS           │ 2. Backend & Data           │ 3. User Platform      │
│ • Text Entry (<=2500) │ • FastAPI REST v1 APIs      │ • Bcrypt Registration │
│ • Live Char/Word Count│ • Uniform JSON Envelopes    │ • Secure JWT Login    │
│ • ISO Language Choice │ • Pydantic v2 Validation    │ • Protected Routes    │
│ • Dynamic Voice Reg.  │ • SQLAlchemy 2.0 ORM        │ • User Profile & Prefs│
│ • ElevenLabs Adapter  │ • PostgreSQL on Render      │ • Generation History  │
│ • Simulation Fallback │ • Alembic Migrations        │ • Bookmarked Favorites│
│ • Streamed Playback   │ • Chunked Range Audio API   │ • Search, Filter, Sort│
│ • Audio Download      │ • Health Endpoint           │ • Pagination          │
├───────────────────────┼─────────────────────────────┼───────────────────────┤
│ 4. Quantum Lab        │ 5. Frontend & UI            │ 6. Engineering/Ops    │
│ • Text Style VQC      │ • React 19 + TypeScript     │ • Secret Isolation    │
│ • Emotion QNN (Penny) │ • Tailwind CSS + Glassmorphism│ • CORS Lockdown     │
│ • State Entanglement  │ • TanStack Query + Zustand  │ • Pytest Backend Suite│
│ • Semantic Kernel Sim │ • Responsive (Mobile/Desktop)│ • Vitest Client Suite │
│ • Circuit Sandbox     │ • Audio Player with Scrubbing│ • GitHub Versioning   │
│ • Noise Simulation    │ • OpenAPI / Swagger UI      │ • Render Backend PaaS │
│ • Honest Benchmarking │ • Postman Collection v2.1   │ • Vercel Frontend Edge│
└───────────────────────┴─────────────────────────────┴───────────────────────┘
```

---

## 3. Implementation Priority Ladder (Section 35)

To prevent architectural collapse and guarantee that foundational subsystems are verified before advanced features are layered on, all subsequent implementation prompts must strictly adhere to the following sequence:

```
┌────────────────────────────────────────────────────────┐
│ Priority 1: Core TTS Pipeline                          │
│ Text input, counters, limits, dynamic voice contract   │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│ Priority 2: Backend Architecture & REST APIs           │
│ FastAPI structure, JSON envelopes, Pydantic validation │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│ Priority 3: Database & Persistence Layer               │
│ SQLAlchemy models, PostgreSQL connection, Alembic      │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│ Priority 4: User Authentication & Security             │
│ Bcrypt hashing, JWT issuance, protected routes         │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│ Priority 5: Responsive Frontend Experience             │
│ React SPA, audio player, voice selector, glass UI      │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│ Priority 6: Speech History, Favorites & Search         │
│ User persistence, filtering, sorting, pagination       │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│ Priority 7: Quantum Intelligence Laboratory            │
│ Qiskit, PennyLane, circuit sandbox, benchmarks         │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│ Priority 8: Quality Assurance & Automated Testing      │
│ Pytest suites, Vitest components, Postman collection   │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│ Priority 9: Cloud Deployment                           │
│ Render (FastAPI + Postgres), Vercel (React frontend)   │
└────────────────────────────────────────────────────────┘
```

> [!IMPORTANT]
> **Priority Invariant:** Never build or modify advanced Quantum UI components while the Core Text-to-Speech foundation is broken or unverified.

---

## 4. Deployment Topology Contract (Section 34)

The production architecture maps directly to the following cloud infrastructure:

```
                            ┌────────────────────────┐
                            │    Vercel Edge SPA     │
                            │   React 19 + Vite      │
                            │   https://bloop.app    │
                            └───────────┬────────────┘
                                        │
                                      HTTPS
                                        │
                            ┌───────────▼────────────┐
                            │  Render Web Service    │
                            │  FastAPI (Python 3.12) │
                            │  api.bloop.internal    │
                            └─────┬────────────┬─────┘
                                  │            │
            ┌─────────────────────┘            └──────────────────────┐
            ▼                                                         ▼
┌───────────────────────────────┐                 ┌───────────────────────────────┐
│       Render PostgreSQL       │                 │      ElevenLabs Cloud API     │
│   Persistent Generation Data  │                 │    Real-Time Audio Synthesis  │
│   Users, Voices, History      │                 │   https://api.elevenlabs.io   │
└───────────────────────────────┘                 └───────────────────────────────┘
```

---

## 5. Explicitly Excluded Features (Anti-Bloat Invariant)

The following features are **explicitly excluded** from the MVP contract:
1. Multi-tenant enterprise organizations and role hierarchies.
2. Subscription billing, checkout carts, or payment gateway integration.
3. Asynchronous job queues (Celery/RabbitMQ) and distributed pub/sub brokers (Kafka).
4. Container orchestration systems (Kubernetes/Helm).
5. Cloud object store SDKs (AWS S3/GCS); audio is stored cleanly on the local service filesystem with HTTP range streaming.
6. Native mobile app builds (iOS / Android).
7. Autonomous AI agents and conversational chatbots.

---

## 6. Contract Verification & Exit Criteria

The Intermediate-Level MVP is formally declared complete when:
1. A new user can register, log in, enter 500 characters of text, choose a language and dynamic voice, and synthesize audio via ElevenLabs.
2. The synthesized audio plays back with seeking and volume controls, and downloads as a valid MP3 file.
3. The generation appears in the user's private history, can be searched by keyword, filtered by language, and bookmarked as a favorite.
4. User B cannot see or manipulate User A's generations or favorites.
5. All 5 Quantum Intelligence modules run successfully on local simulators and generate transparent benchmark metrics without errors.
6. The entire automated test suite passes with zero regressions.
7. The full stack is deployed live on Render and Vercel and communicates via HTTPS without CORS errors.
