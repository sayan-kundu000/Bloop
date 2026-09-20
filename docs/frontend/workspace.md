# Bloop Text Workspace, Dynamic Language/Voice Selection & Responsive UX

## 1. Architectural Overview

The Bloop Text Workspace (`src/features/tts/`) is the central creative environment for text-to-speech authoring. It coordinates multiline text editing, live character and word metrics, client-side validation, dynamic language selection, and dynamic voice selection.

```mermaid
flowchart TD
    A[User] --> B[Bloop Text Workspace]

    B --> C[Text Editor (Textarea)]
    B --> D[Text Metrics (Char / Word / Duration)]
    B --> E[Language Selector]
    B --> F[Voice Selector]

    E --> G[GET /api/v1/languages]
    F --> H[GET /api/v1/voices]

    G --> I[FastAPI Backend]
    H --> I

    B --> J[Validation Engine]
    J --> K[Generation Ready State]

    K --> L[Future Speech Generation Flow (Prompt 19)]
```

---

## 2. Component Composition

The workspace avoids monolithic structure by employing clean sub-component composition:

```text
src/features/tts/
├── components/
│   ├── TextWorkspace.tsx            # Master coordinator & generation handoff
│   ├── TextEditor.tsx               # Semantic <textarea> with accessible labeling
│   ├── TextMetrics.tsx              # Live character (X / MAX), word, and duration counter
│   ├── TextValidationMessage.tsx     # Contextual alert for errors & limit states
│   ├── WorkspaceToolbar.tsx         # Clear (with confirmation), preset samples, paste
│   ├── WorkspaceEmptyState.tsx      # Guidance banner when text is empty
│   ├── LanguageSelector.tsx         # Dynamic dropdown with loading/empty/error states
│   ├── VoiceSelector.tsx            # Dynamic dropdown with language compatibility filter
│   └── SelectionSummary.tsx         # Concise badge summary of active language & voice
├── hooks/
│   ├── useLanguages.ts              # TanStack Query hook for /api/v1/languages
│   ├── useVoices.ts                 # TanStack Query hook for /api/v1/voices
│   ├── useTextMetrics.ts            # Reactive metrics calculation hook
│   └── useWorkspaceValidation.ts    # Consolidated validation & canGenerate check
├── utils/
│   ├── textMetrics.ts               # Pure counting and duration calculation utilities
│   └── textValidation.ts            # Validation rules and voice-language compatibility
├── types/
│   └── tts.types.ts                 # Feature domain types and payload definitions
├── api/
│   └── tts.api.ts                   # Typed API client functions
└── index.ts                         # Public barrel export
```

---

## 3. Dynamic Language & Voice Architecture

### Strict Voice Invariant
- **No Hardcoded Voices**: The frontend never hardcodes ElevenLabs voice IDs or names (e.g. "Rachel", "Adam").
- **Dynamic Retrieval**: All voices and languages are loaded dynamically via TanStack Query from `/api/v1/languages` and `/api/v1/voices`.
- **Empty State as First-Class Citizen**: When the database contains zero voices or zero languages, the UI gracefully displays clean empty states without inventing fake catalog entries.

### Language $\rightarrow$ Voice Dependency
When the user changes the selected language:
1. `VoiceSelector` filters available voices to only those that support the chosen language locale (via `supported_languages` array or primary `language_code`).
2. If the currently selected voice does not support the newly chosen language, `voiceId` is immediately cleared to `null` / `""`.
3. `canGenerate` transitions to `false` until a compatible voice is selected, preventing invalid combinations from reaching the backend.

---

## 4. Text Metrics & Validation

### Deterministic Counting
- **Characters**: Exact `text.length` (including whitespace, newlines, and unicode).
- **Words**: Deterministic regex tokenization `text.trim().split(/\s+/)`, returning `0` for empty or whitespace-only text.
- **Estimated Duration**: Calculated at ~150 words per minute (2.5 words/sec), scaled by the user's active playback speed setting.

### Limits & Progress
- Maximum characters is mirrored directly from configuration (`config.limits.maxTextLength` = 2,500).
- Progress bar transitions visually:
  - Normal: Bloop violet (`bg-bloop-500`)
  - $\ge 85\%$ used: Warning amber (`bg-amber-500`)
  - $> 100\%$ used: Error rose (`bg-rose-500`) with alert banner

### Preservation of User Content
Validation uses `text.trim()` to ensure non-whitespace characters exist, but the original text string is preserved exactly for generation without cosmetic trimming or silent transformation.

---

## 5. Responsive UX & Accessibility

- **Responsive Grid**:
  - Desktop: Multi-column workspace layout with side-by-side language and voice selectors.
  - Tablet & Mobile: Stacked layout with touch-friendly select elements, no horizontal overflow, and auto-expanding textarea.
- **WCAG 2.1 AA Compliance**:
  - Explicit `<label>` elements linked to inputs via `htmlFor`.
  - Accessible character progress bar with `role="progressbar"` and `aria-valuenow`.
  - Live regions for validation feedback with `role="alert"`.
  - Full keyboard navigability (Tab, Shift+Tab, Enter, Space, Escape on dialogs).
