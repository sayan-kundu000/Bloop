# Bloop — Frontend Architecture Specification

**Document Identifier:** BLOOP-FRONTEND-ARCH-V1  
**Project:** Bloop — AI Text-to-Speech & Quantum Intelligence Platform  
**Target Milestone:** Intermediate-Level Frontend Architecture  
**Status:** Approved Technical Design  
**Authority:** Bloop Master Prompt & Prompt 02  

---

## 1. Executive Frontend Overview

The Bloop frontend is a responsive, high-performance Single Page Application (SPA) built with **React 19**, **TypeScript**, **Vite**, and **Tailwind CSS**. It delivers an interactive text-to-speech workspace with live text metrics, an integrated persistent audio player, multi-tenant history and bookmark management, and an educational Quantum Intelligence Laboratory.

```
Pages (React Router)
  │
  ▼
Feature Components (TTS, History, Favorites, Quantum)
  │
  ▼
Shared UI Components (Button, Modal, Input, Badge, Toast)
  │
  ▼
Custom Hooks (useAudioPlayer, useTTSWorkspace, useDebounce)
  │
  ├───────────────────────────────┐
  ▼                               ▼
Client State (Zustand)    Server State (TanStack Query)
  │                               │
  └───────────────┬───────────────┘
                  │
                  ▼
          API Client (Axios)
                  │
                  ▼
         REST API (/api/v1/*)
```

---

## 2. Technology Stack & Key Libraries

| Capability | Library / Technology | Version | Architectural Role |
| :--- | :--- | :--- | :--- |
| **Framework** | React | 19.x | Component lifecycle, declarative UI rendering, concurrent features. |
| **Language** | TypeScript | 5.x | Static typing, interface contracts matching backend Pydantic schemas. |
| **Bundler & Dev Server** | Vite | 6.x | Near-instant Hot Module Replacement (HMR) and optimized rollup production bundles. |
| **Styling** | Tailwind CSS | 3.4+ | Utility-first responsive design, dark/light theme tokens, micro-interactions. |
| **Routing** | React Router | 7.x | Declarative client-side routing, nested layouts, protected route guards. |
| **Server State** | TanStack Query | 5.x | Data caching, query deduplication, background synchronization, mutation lifecycles. |
| **Client State** | Zustand | 5.x | Lightweight, decoupled global UI stores (audio player, authentication, layout). |
| **HTTP Client** | Axios | 1.7+ | HTTP communication, Bearer token interceptor, standard JSON envelope extraction. |
| **Icons** | Lucide React | Latest | Consistent, lightweight SVG iconography. |

---

## 3. Logical Directory Structure

```
frontend/
├── public/                 # Static public assets, favicon, audio samples
├── src/
│   ├── api/                # HTTP client & API service functions
│   │   ├── client.ts       # Axios instance with auth interceptors & error unboxing
│   │   ├── tts.ts          # TTS generation, audio fetch, voice/language queries
│   │   ├── auth.ts         # Login, register, profile queries
│   │   ├── history.ts      # History list, filter, search, delete mutations
│   │   ├── favorites.ts    # Favorites CRUD mutations
│   │   └── quantum.ts      # Quantum text, emotion, semantic, circuit, benchmark queries
│   │
│   ├── components/         # Component tree
│   │   ├── common/         # Shared primitives (Button, Modal, Input, Spinner, Toast)
│   │   ├── layout/         # AppLayout, Navbar, Sidebar, Footer, ProtectedRoute
│   │   ├── tts/            # TextWorkspace, LiveCounters, VoiceSelector, AudioPlayerBar
│   │   ├── history/        # HistoryTable, HistoryCard, FilterToolbar, DetailModal
│   │   ├── favorites/      # FavoriteGrid, FavoriteCard, NoteEditor
│   │   └── quantum/        # QuantumVisualizer, QubitCircuitCanvas, BenchmarkChart
│   │
│   ├── hooks/              # Custom React hooks
│   │   ├── useAudioPlayer.ts   # Audio playback, seeking, volume, range synchronization
│   │   ├── useTTSWorkspace.ts  # Input debounce, live character/word/duration counters
│   │   ├── useVoices.ts        # TanStack query hook for dynamic voice/language fetching
│   │   └── useDebounce.ts      # Input debouncing for history search
│   │
│   ├── pages/              # Top-level route pages
│   │   ├── WorkspacePage.tsx   # Core TTS synthesis studio
│   │   ├── HistoryPage.tsx     # Full generation history with search/filters
│   │   ├── FavoritesPage.tsx   # Saved bookmark collections
│   │   ├── QuantumLabPage.tsx  # Multi-tab Quantum Intelligence laboratory
│   │   ├── LoginPage.tsx       # Authentication login view
│   │   ├── RegisterPage.tsx    # User registration view
│   │   └── ProfilePage.tsx     # User preferences & default voice selection
│   │
│   ├── stores/             # Zustand client-state stores
│   │   ├── authStore.ts    # Token storage, user identity, login/logout actions
│   │   ├── playerStore.ts  # Current audio track, play/pause state, volume, scrubber
│   │   └── uiStore.ts      # Sidebar toggle, theme mode, active modals
│   │
│   ├── types/              # TypeScript declarations mirroring backend schemas
│   │   ├── tts.ts          # TTSRequest, TTSResponse, Voice, Language
│   │   ├── auth.ts         # User, TokenResponse, LoginRequest
│   │   ├── history.ts      # SpeechGeneration, HistoryFilterParams, Pagination
│   │   └── quantum.ts      # QuantumTextResult, EmotionQNNResult, BenchmarkResult
│   │
│   ├── utils/              # Helper utilities
│   │   ├── formatters.ts   # Time (mm:ss), date, and byte formatting
│   │   └── validation.ts   # Text length, character trimming, empty checks
│   │
│   ├── App.tsx             # Route configuration, QueryClientProvider, ToastContainer
│   ├── main.tsx            # React DOM root render
│   └── index.css           # Tailwind directives and CSS variables
```

---

## 4. Feature Domain Architecture

The application is decomposed into distinct, cohesive feature domains:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND FEATURE DOMAINS                          │
├─────────────────┬───────────────────────────────────────────────────────────┤
│ Domain          │ Key Components & Responsibilities                         │
├─────────────────┼───────────────────────────────────────────────────────────┤
│ **auth/**       │ Manages JWT authentication lifecycle. ProtectedRoute     │
│                 │ redirects unauthenticated requests to `/login`.            │
├─────────────────┼───────────────────────────────────────────────────────────┤
│ **tts/**        │ Primary studio workspace. Real-time character/word        │
│                 │ counters, estimated audio duration, language dropdown,    │
│                 │ dynamic voice selector, and audio generation trigger.     │
├─────────────────┼───────────────────────────────────────────────────────────┤
│ **player/**     │ Persistent floating audio bar. HTML5 audio controller,    │
│                 │ play/pause, seek scrubber, volume slider, download button.│
├─────────────────┼───────────────────────────────────────────────────────────┤
│ **history/**    │ Multi-tenant generation log. Server-side pagination,      │
│                 │ debounced text search, filter by language/voice/date.     │
├─────────────────┼───────────────────────────────────────────────────────────┤
│ **favorites/**  │ Filtered view of user-bookmarked audio generations.       │
│                 │ Quick-play controls, bookmark toggling, custom notes.     │
├─────────────────┼───────────────────────────────────────────────────────────┤
│ **profile/**    │ User profile management, default language/voice selection, │
│                 │ account statistics, and UI theme preferences.             │
├─────────────────┼───────────────────────────────────────────────────────────┤
│ **quantum/**    │ Dedicated multi-panel Quantum Lab: Text Classifier (VQC), │
│                 │ Emotion QNN, Semantic Kernel, Circuit Sandbox, Benchmark. │
└─────────────────┴───────────────────────────────────────────────────────────┘
```

---

## 5. State Management Rules

### 5.1 Server-State Rule (TanStack Query)
All asynchronous server state is managed exclusively by **TanStack Query**. It handles caching, deduplication, re-fetching on window focus, and background mutation lifecycles.

**Standard Query Keys:**
- `['voices', languageCode]`: Available voices for selected language.
- `['languages']`: Supported ISO language locales.
- `['history', { page, pageSize, search, language, voice }]`: Filtered history list.
- `['favorites']`: User bookmarked items.
- `['user', 'me']`: Authenticated user profile and preferences.

**Mutations with Automatic Cache Invalidation:**
- `generateSpeechMutation`: On success, invalidates `['history']` and updates `playerStore` with new audio.
- `toggleFavoriteMutation`: On success, invalidates `['favorites']` and `['history']`.
- `deleteHistoryMutation`: On success, invalidates `['history']` and `['favorites']`.

### 5.2 Client-State Rule (Zustand)
Zustand is reserved strictly for **client-side ephemeral state**. It must never duplicate or mirror server state returned by TanStack Query.

**Zustand Stores:**
1. `authStore`: Access token, user identity, `isAuthenticated` flag, login/logout handlers.
2. `playerStore`: Currently loaded audio URL, playing state, current timestamp, total duration, volume, playback speed (0.75x to 2x).
3. `uiStore`: Sidebar collapse state, theme (dark/light), active modals (e.g., Dynamic Voice Ingestion modal).

---

## 6. Frontend Data Flow for Speech Synthesis

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant WS as TextWorkspace (UI)
    participant Hook as useTTSWorkspace
    participant Mutation as TanStack Query Mutation
    participant API as Axios API Client
    participant Backend as FastAPI (/api/v1/tts)
    participant Player as playerStore (Zustand)
    participant PlayerBar as AudioPlayerBar (UI)

    User->>WS: Enters text in input area
    WS->>Hook: Computes live character count, word count, estimated duration
    Hook-->>WS: Updates counter badges (e.g. 240 / 2,500 chars)
    User->>WS: Selects language & voice, clicks "Generate Speech"
    WS->>WS: Client validation (length >= 1, <= 2500, voice selected)
    WS->>Mutation: mutate({ text, language, voice_id })
    Mutation->>API: POST /api/v1/tts (Bearer JWT)
    API->>Backend: HTTP POST /api/v1/tts
    Backend-->>API: HTTP 200 { success: true, data: { id, audio_url, download_url, duration } }
    API-->>Mutation: Resolves with TTSResponse
    Mutation->>Player: loadAudio(audio_url, download_url, title)
    Mutation->>Mutation: Invalidate ['history'] query cache
    Player->>PlayerBar: Updates audio source, auto-plays stream
    PlayerBar-->>User: Audio begins playing; scrubber active; download unlocked
```

---

## 7. Audio Player Architecture

The audio subsystem is powered by a persistent, global audio controller:
- **Audio Element Hook (`useAudioPlayer`):** Maintains a singleton reference to an HTML5 `Audio` instance.
- **HTTP 206 Partial Content Compatibility:** Communicates with backend audio streaming endpoints using standard byte-range requests, allowing instant scrub navigation without loading the full file.
- **Controls & Capabilities:**
  - Play / Pause toggling with keyboard shortcuts (Spacebar).
  - Continuous seek scrubber with millisecond precision and smooth dragging.
  - Volume slider with persistent local storage and mute toggle.
  - Playback speed adjustment (0.75x, 1.0x, 1.25x, 1.5x, 2.0x).
  - Direct file download triggering `GET /api/v1/tts/download/{filename}`.
  - Duration display formatted cleanly as `mm:ss`.

---

## 8. Dynamic Voice Ingestion Modal Architecture

To fulfill the **Dynamic Voice Architecture** without hardcoding vendor IDs:
1. Users can open the **"Add Custom Voice"** modal directly from the voice selector.
2. The modal captures:
   - Voice ID (e.g. valid ElevenLabs string).
   - Display Name.
   - ISO Language Locale (`en-US`, `es-ES`, etc.).
   - Gender / Category / Accent tags.
3. Submitting triggers `POST /api/v1/voices`.
4. On success, TanStack Query invalidates `['voices']`, immediately populating the selector with the newly registered voice.

---

## 9. API Client & HTTP Interceptor Architecture

The Axios client (`src/api/client.ts`) enforces the frontend security and communication contract:
1. **Base URL Configuration:** Automatically loads `VITE_API_BASE_URL` from the environment (defaulting to `http://localhost:8000`).
2. **Request Interceptor:** Automatically injects the active Bearer token into the `Authorization` header:
   ```typescript
   config.headers.Authorization = `Bearer ${token}`;
   ```
3. **Response Interceptor (Envelope Unboxing):** Checks the standard response structure (`success: boolean`). If `success === true`, it unwraps `response.data.data`.
4. **Error Interceptor:** Intercepts HTTP 401 Unauthorized responses, purges the invalid token from `authStore`, and redirects the user to `/login` with an informative toast notification.

---

## 10. Error Boundaries & Defensive UI

1. **Root Error Boundary:** Catches uncaught runtime exceptions in the React tree, displaying an accessible fallback screen with a "Reload Application" action.
2. **Component-Level Error Fallbacks:** Isolated sections (such as the Quantum Lab canvas or History Table) feature localized error cards that prevent a single widget failure from crashing the entire page.
3. **Pulsing Skeleton States:** All data-fetching views (Voices dropdown, History list, Favorites grid) display animated skeleton cards while queries are pending, preventing layout shifts.
