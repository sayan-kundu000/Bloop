# ADR-021: Bloop Text Workspace, Dynamic Language/Voice Selection & Responsive UX

## Status
**Approved** (Implemented in Prompt 18)

---

## Context
Bloop requires a central text-to-speech authoring workspace where users enter speech text, receive real-time metrics, select compatible languages and voices dynamically, and prepare valid payloads for the synthesis pipeline.

Previous prompts established the backend API contracts (`/api/v1/languages`, `/api/v1/voices`, `/api/v1/tts`), database schemas, and frontend UI foundation (React 19, TypeScript, Tailwind, TanStack Query, Zustand). This prompt builds the specialized TTS workspace layer on top of that foundation.

---

## Decision

### 1. Domain-Oriented Architecture
We establish `frontend/src/features/tts/` containing:
- Focused UI sub-components (`TextEditor`, `TextMetrics`, `TextValidationMessage`, `LanguageSelector`, `VoiceSelector`, `SelectionSummary`, `WorkspaceToolbar`, `WorkspaceEmptyState`, and the `TextWorkspace` coordinator).
- Custom TanStack Query hooks (`useLanguages`, `useVoices`).
- Pure calculation and validation utilities (`textMetrics`, `textValidation`).
- Domain types (`tts.types.ts`) and API client (`tts.api.ts`).

### 2. Strict Voice Invariant
We strictly prohibit hardcoding real or fictional ElevenLabs voice IDs or names in the frontend. All voices are fetched dynamically via TanStack Query from `/api/v1/voices`. Empty voice catalogs are supported as first-class states.

### 3. Language $\rightarrow$ Voice Dependency
When the selected language changes:
- Available voices in `VoiceSelector` are filtered to only those that support the chosen language (matching `supported_languages` or primary `language_code`).
- If the currently selected voice does not support the new language, `voiceId` is reset to `null` / `""`.
- The `Generate Speech` action remains disabled until a compatible voice is selected.

### 4. Preservation of User Content
Text content entered by the user is never automatically trimmed, paraphrased, or modified for generation. Validation verifies that meaningful text exists using `text.trim()`, but passes the exact string to the synthesis API.

### 5. Configuration-Driven Metrics
Character limits are derived directly from centralized configuration (`config.limits.maxTextLength` = 2,500). Word counts are computed deterministically using whitespace tokenization.

### 6. Generation Readiness Handoff
The workspace computes a derived `canGenerate` boolean flag (`text valid && language selected && voice selected && voice compatible`), establishing a clean callback boundary (`onGenerate`) for Prompt 19 (Speech Generation UX).

---

## Consequences

### Positive
- **High Cohesion**: Sub-components remain small (< 150 lines), testable, and focused.
- **Provider Decoupling**: Frontend remains decoupled from third-party speech engines.
- **Immediate UX Feedback**: Users see live character progress and validation alerts before initiating expensive API calls.
- **Accessibility**: Semantic HTML and ARIA landmarks provide full WCAG 2.1 AA compliance.

### Negative / Trade-offs
- Changing languages requires clearing incompatible voices, requiring the user to re-select a voice if their previous choice was locale-specific.
