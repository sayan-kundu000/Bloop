# Bloop — Frontend Application Architecture

The Bloop frontend is a responsive Single Page Application (SPA) built with **React 19**, **TypeScript**, **Vite**, and **Tailwind CSS**. It delivers an interactive text-to-speech studio with live character/word counters, a persistent floating audio player, multi-tenant history, and an educational Quantum Intelligence Laboratory.

```
frontend/
├── public/                 # Static public assets
├── src/
│   ├── app/                # Root providers (QueryClientProvider, Theme)
│   ├── assets/             # Brand logos, icons, SVG graphics
│   ├── components/         # Reusable UI primitives (Button, Modal, Input, Badge)
│   ├── features/           # Domain features (tts, history, favorites, quantum)
│   ├── hooks/              # Custom React hooks (useAudioPlayer, useTTSWorkspace, useDebounce)
│   ├── layouts/            # AppLayout, Navbar, Sidebar, Footer, ProtectedRoute
│   ├── lib/                # Third-party configurations (queryClient, axios)
│   ├── pages/              # Route pages (WorkspacePage, HistoryPage, QuantumLabPage)
│   ├── services/           # API communication service functions
│   ├── stores/             # Zustand client-only state stores (playerStore, authStore)
│   ├── types/              # TypeScript types mirroring backend Pydantic schemas
│   ├── utils/              # Pure utility functions (formatters, validation)
│   ├── App.tsx             # Application router & layout composition
│   └── main.tsx            # DOM root entrypoint
├── tests/                  # Vitest unit & component test suite
├── package.json            # Node dependencies and build scripts
├── vite.config.ts          # Vite build and plugin configuration
├── tailwind.config.js      # Tailwind CSS design tokens
├── vercel.json             # Vercel SPA routing rewrite rules
└── .env.example            # Environment configuration template
```

## State Management Rules
- **Server State:** Managed exclusively via **TanStack Query v5** (`useQuery`, `useMutation`).
- **Client UI State:** Managed exclusively via **Zustand v5** (`playerStore`, `authStore`, `uiStore`).
- **Anti-Duplication Invariant:** Zustand stores must **never** mirror or duplicate server data from TanStack Query.

## Quickstart

```bash
# Install dependencies
npm install

# Start Vite development server
npm run dev

# Run Vitest test suite
npm test

# Build for production
npm run build
```
