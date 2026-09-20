# Frontend Testing Foundation

## 1. Testing Stack & Strategy

Bloop's frontend testing suite utilizes **Vitest** and **React Testing Library** (RTL), configured with **JSDOM** and `@testing-library/jest-dom`.

Testing prioritizes **user observable behavior** over internal implementation details:
- Can the user type speech text and observe character count updates?
- Does clicking "Generate Speech" disable the button and show a spinner?
- Does unauthenticated access to `/workspace` redirect to `/login`?
- Does a rate-limited response (HTTP 429) display a polite error banner?
- Does pressing Escape dismiss an open modal?

---

## 2. Test Directory Architecture

```text
src/test/
├── setup.ts                    # Vitest global setup & browser polyfills
├── utils/
│   └── test-utils.tsx          # Custom render with isolated QueryClient & MemoryRouter
├── fixtures/
│   └── index.ts                # Mock users, speech generations, dynamic voices
├── mocks/
│   └── apiMock.ts              # Vi-mocked API modules
├── components/
│   └── ui.test.tsx             # Unit tests for UI primitives
├── routes/
│   └── routing.test.tsx        # Route guard & 404 tests
└── api/
    └── client.test.ts          # API client & FrontendApiError tests
```

---

## 3. QueryClient Isolation in Tests

To guarantee tests never leak cached query data or state between runs, `src/test/utils/test-utils.tsx` generates a fresh, isolated `QueryClient` for every render:

```typescript
export function createTestQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
      mutations: { retry: false },
    },
  });
}
```

---

## 4. Mocking Policy & Isolation

1. **No External Network Calls**:
   Unit and component tests never call ElevenLabs, Render, or production URLs.
2. **Dynamic Voices Mocking**:
   Test fixtures provide dynamic mock voice objects with neutral IDs (`dynamic-test-voice-1`). Zero real ElevenLabs voice IDs or hardcoded catalogs are placed in fixtures.
3. **Audio Mocking**:
   `setup.ts` polyfills `HTMLMediaElement.prototype.play()` and `pause()` to ensure audio controls test without browser audio device exceptions.

---

## 5. Test Commands

```bash
# Run Vitest test suite once
npm run test

# Run Vitest in watch mode during development
npm run test -- --watch
```
