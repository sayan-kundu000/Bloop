# ADR-009: Strict State Management Separation: TanStack Query for Server State and Zustand for Client State

## Status
**Accepted**

## Context
State management in modern full-stack web applications frequently suffers from anti-patterns:
1. Re-implementing network caching, deduplication, retry loops, and cache invalidation inside global client stores (e.g. Redux, raw Zustand).
2. Duplicating backend database records in client state, leading to stale data, sync bugs, and bloated memory.
3. Over-complicating purely local UI state (e.g. sidebar collapse, modal visibility, current audio track) with boilerplate-heavy reducers.

## Decision
Establish a strict, non-negotiable two-tier state management policy:
1. **Server State (TanStack Query 5.x):** All asynchronous data retrieved from or persisted to the backend (user profiles, available voices, language locales, speech history, favorites, quantum results) is managed exclusively by **TanStack Query**.
2. **Client State (Zustand 5.x):** Ephemeral client-only UI state (audio player playback status, volume slider, sidebar toggle, active theme, modal visibility) is managed exclusively by **Zustand**.
3. **Local Component State (React `useState` / `useRef`):** Ephemeral text input values, character counter debouncing, and local form validations remain inside component hooks.
4. **Anti-Duplication Invariant:** Zustand stores must **never** mirror, duplicate, or cache server state returned by TanStack Query.

## Alternatives Considered
1. **Redux Toolkit (RTK + RTK Query):** Mature and powerful, but introduces high boilerplate, complex slice configurations, and unnecessary runtime weight for an intermediate-level SPA.
2. **Zustand Only (Manual Async Actions):** Using Zustand `create()` with manual `fetch()` calls and storing `isLoading`, `data`, and `error` manually in Zustand stores. Rejected because it forces manual implementation of cache invalidation, deduplication, background refetching, and pagination tracking.
3. **React Context Only:** Built-in without external dependencies, but causes unnecessary whole-tree re-renders whenever state changes, causing audio player glitches and counter lag during rapid typing.

## Consequences

### Positive
- **Automatic Caching & Invalidation:** TanStack Query automatically deduplicates simultaneous requests, caches voice/language lists, and invalidates history queries (`queryClient.invalidateQueries({ queryKey: ['history'] })`) upon new speech generations or deletions.
- **Micro-State Reactivity:** Zustand provides selector-based subscriptions (`usePlayerStore(state => state.isPlaying)`), ensuring audio playback controls update without re-rendering the heavy text workspace or quantum visualization canvas.
- **Zero State Duplication:** Eliminates out-of-sync bugs between client cache and server database.

### Negative / Trade-offs
- **Mental Model Discipline:** Developers must actively discern whether a piece of data originates from the server (TanStack Query) or is purely ephemeral client UI state (Zustand).
