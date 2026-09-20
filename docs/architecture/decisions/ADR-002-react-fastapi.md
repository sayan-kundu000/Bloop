# ADR-002: React 19 SPA Frontend and FastAPI Asynchronous Backend

## Status
**Accepted**

## Context
Bloop delivers real-time audio playback, interactive text workspaces, responsive character/word counters, visual quantum circuit simulations, and rapid speech synthesis requests. We needed to choose the frontend rendering model and backend web framework that satisfy these interactive requirements while supporting modern Python-based quantum computing libraries (Qiskit, PennyLane).

Alternatives considered:
- **Frontend:** Server-Side Rendered (Next.js / Remix) vs. Client-Side SPA (React + Vite).
- **Backend:** Node.js (Express/NestJS) vs. Python (Django, Flask, FastAPI).

## Decision
1. **Frontend:** Adopt **React 19 + TypeScript + Vite + Tailwind CSS** as a pure client-side Single Page Application (SPA).
2. **Backend:** Adopt **Python 3.11+ with FastAPI + Uvicorn + Pydantic v2 + SQLAlchemy 2.0**.

## Rationale
1. **Python Quantum Ecosystem:** Qiskit, Qiskit Aer, PennyLane, Scikit-Learn, and NumPy are native to Python. Building the backend in Python avoids inter-process bridges, microservices, or RPC layers to separate quantum runtimes.
2. **FastAPI Performance & Async I/O:** FastAPI provides native asynchronous I/O (`async`/`await`), allowing non-blocking HTTP calls to ElevenLabs and efficient streaming of chunked audio data.
3. **Automatic OpenAPI/Swagger Generation:** FastAPI generates interactive OpenAPI schemas and Swagger UI (`/docs`) directly from Pydantic models, keeping backend and frontend types in sync.
4. **SPA Responsiveness:** The Bloop audio player, waveform visualizers, live counters, and quantum circuit canvas require rich in-browser reactivity that benefits from an SPA model rather than server-side page reloads.
5. **Static Hosting Simplicity:** A Vite SPA compiles to pure static HTML/JS/CSS, deployable on Vercel's global edge network at zero compute cost.

## Consequences
### Positive
- Unified Python runtime for business services, ElevenLabs integration, and quantum execution.
- High-throughput asynchronous request processing.
- Automatic request/response validation with Pydantic v2.
- Low-latency frontend state transitions without server round-trips.

### Negative / Trade-offs
- Client-side rendering requires initial JavaScript bundle download (mitigated with Vite code-splitting).
- SEO is limited compared to SSR (acceptable as Bloop is an authenticated interactive web platform).
