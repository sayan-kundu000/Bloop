# ADR-001: Selection of React and TypeScript for Frontend Architecture

## Status
**Accepted**

## Context
Bloop is a web-based artificial intelligence platform that combines commercial AI speech synthesis with an educational Quantum Intelligence Laboratory. The user interface requires high interactivity: real-time character and word counters, estimated audio duration updates on every keystroke, dynamic voice selection, persistent audio playback with waveform/scrubbing controls, and visual quantum circuit and benchmark rendering.

We evaluated frontend frameworks and type systems to balance rapid development, interactive responsiveness, client-side performance, and long-term maintainability.

## Decision
Adopt **React 19** paired with **TypeScript 5.x** and **Vite** as the standard frontend architecture.

## Alternatives Considered
1. **Vue 3 + TypeScript:** Excellent reactivity and single-file components, but a smaller ecosystem for specialized quantum/scientific visualization components and fewer developers familiar with advanced React state orchestration.
2. **SvelteKit / SolidJS:** Outstanding compile-time reactivity and performance, but narrower community adoption and less mature enterprise UI primitives compared to the React ecosystem.
3. **Vanilla JavaScript (No TypeScript):** Faster initial scaffolding, but introduces severe runtime fragility, inability to statically mirror backend Pydantic schemas, and high regression risk across complex state stores.
4. **Next.js (React Server Components / SSR):** High initial complexity, unnecessary Node.js server overhead on Vercel, and complexity with purely client-side audio streaming and statevector simulation canvases.

## Consequences

### Positive
- **Static Type Safety:** TypeScript types directly mirror backend Pydantic schemas (`TTSRequest`, `TTSResponse`, `Voice`, `QuantumTextResult`), eliminating schema drift and serialization errors at compile time.
- **Component Reusability:** Modular UI composition for workspace text inputs, audio player bars, dynamic voice ingestion modals, and quantum visualization canvases.
- **Rich Community Ecosystem:** Native support for Lucide icons, Tailwind CSS, TanStack Query, and audio manipulation libraries.
- **Fast Developer Feedback:** Vite HMR provides instant feedback (<50ms) during UI development.

### Negative / Trade-offs
- **Initial Bundle Size:** Requires client-side JavaScript execution (mitigated by Vite tree-shaking and dynamic code-splitting).
- **Compilation Overhead:** TypeScript requires strict compilation checks during CI/CD (`tsc -b`), requiring disciplined type maintenance across all developers.
