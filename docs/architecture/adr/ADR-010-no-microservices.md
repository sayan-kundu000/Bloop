# ADR-010: Rejection of Microservices in Favor of a Modular Monolithic Backend

## Status
**Accepted**

## Context
Full-stack applications that combine multiple domains (authentication, text-to-speech synthesis, relational history, and quantum simulation) are sometimes architected into distributed microservices (e.g., an Auth Service, a TTS Gateway, a Database Service, and a separate Quantum Compute Worker communicating via Kafka or RabbitMQ).

We evaluated whether a distributed microservice architecture is warranted for Bloop.

## Decision
Explicitly reject microservices and distributed queue brokers. Adopt a **Modular Monolithic Backend** deployed as a single FastAPI web service on Render, backed by a single PostgreSQL database.

## Alternatives Considered
1. **Distributed Microservices with gRPC / REST:** Splitting TTS, Auth, and Quantum into separate deployable containers. Rejected because it introduces distributed tracing complexity, inter-service network failure modes, multiple deployment pipelines, increased cloud hosting costs, and distributed transaction issues (2PC / Sagas).
2. **Asynchronous Task Workers via Celery / Redis:** Offloading quantum simulations and ElevenLabs synthesis to Celery worker containers backed by Redis. Rejected because it adds three additional cloud services to deploy and monitor (Redis instance, Celery worker pool, Celery flower) for operations that FastAPI's native `asyncio` event loop and bounded execution limits already handle cleanly within a single process.
3. **Serverless Functions (AWS Lambda / Google Cloud Functions):** Running backend routes as serverless functions. Rejected because heavy scientific libraries (Qiskit Aer, PennyLane, SciPy, NumPy) exceed serverless package size limits (250 MB unzipped) and suffer from severe cold-start latencies (10–30 seconds) on every quantum circuit compilation.

## Consequences

### Positive
- **Operational Simplicity:** A single GitHub commit triggers a single build and deployment on Render. Developers run a single Python command locally (`uvicorn app.main:app`) to start the entire backend.
- **In-Memory Performance:** Communication between services (e.g. `TTSService` reading from `VoiceRepository`) executes in-memory via direct Python method calls rather than over network serialization boundaries.
- **Single Database Integrity:** All tables (`users`, `voices`, `speech_generations`, `favorites`, `quantum_experiments`) share a unified PostgreSQL transaction context and connection pool.
- **Bounded Quantum Safety:** Strict computational bounds ($\le 8$ qubits, $\le 1024$ shots, 15s timeout) allow quantum simulations to execute safely in-process without overwhelming CPU or memory limits.

### Negative / Trade-offs
- **Single Point of Deployment:** A fatal crash in the backend process could temporarily affect both speech synthesis and quantum endpoints (mitigated by strict exception isolation and defensive try-catch boundaries).
- **Horizontal Scaling Granularity:** The entire monolith scales together rather than scaling the quantum engine independently from the speech engine (acceptable given the intermediate-level traffic and resource bounds).
