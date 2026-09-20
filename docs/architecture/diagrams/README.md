# Bloop — Architecture Diagrams Catalog

This directory catalogs the visual Mermaid diagrams modeling the Bloop system architecture across all domains:

## 1. System Topology (C4 Container View)
See [System Architecture Specification](../system-architecture.md#3-high-level-system-topology-c4-container-view).
Visualizes the relationship between the User Browser, Vercel Edge SPA, Render FastAPI Web Service, Render PostgreSQL 16, ElevenLabs API, and the in-process Quantum Intelligence Core.

## 2. End-to-End Speech Synthesis Flow
See [TTS Data Flow Specification](../tts-data-flow.md#2-the-21-step-canonical-tts-execution-flow).
A detailed 21-step sequence diagram from initial user keystroke to dual-layer validation, ElevenLabs HTTPS mediation, server disk storage, and HTTP 206 Partial Content byte streaming.

## 3. Database Entity-Relationship Diagram (ERD)
See [Database Architecture Specification](../database-architecture.md#2-entity-relationship-diagram-erd).
Models all relational entities: `users`, `languages`, `voices`, `speech_generations`, `favorites`, `user_preferences`, and `quantum_experiments`.

## 4. Frontend Layer & State Architecture
See [Frontend Architecture Specification](../frontend-architecture.md#1-executive-frontend-overview).
Illustrates the unidirectional data flow between Pages, Feature Components, Shared Primitives, Custom Hooks, Zustand UI stores, TanStack Query server cache, and Axios REST clients.

## 5. Quantum Intelligence Subsystem Flow
See [Quantum Architecture Specification](../quantum-architecture.md#4-complete-quantum-data-flow).
Details feature vector extraction, Hilbert angle encoding, parameterized rotation layers, Aer/PennyLane simulators, and result normalization.

## 6. Cloud PaaS Deployment Topology & CI/CD
See [Deployment Architecture Specification](../deployment-architecture.md#1-executive-deployment-overview) and [Technology Stack](../technology-stack.md#2-visual-architecture-diagram).
Visualizes the continuous delivery pipeline from GitHub push to parallel Vercel Edge builds and Render web service deployments with automated database migrations.
