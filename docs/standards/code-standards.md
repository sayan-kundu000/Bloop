# Bloop — Codebase Standards & Engineering Guidelines

**Document Identifier:** BLOOP-STANDARDS-V1  
**Authority:** Bloop Master Prompt & Prompt 04  

---

## 1. Python Code Standards (`backend/`)

- **Python Version:** 3.11+ / 3.12.
- **Type Annotations:** All function signatures and class methods must use explicit type annotations. Use Python 3.10+ union syntax (`str | None` instead of `Optional[str]`).
- **Pydantic v2:** All request and response models must inherit from `pydantic.BaseModel` with explicit field types and docstrings.
- **SQLAlchemy 2.0:** All database models must inherit from `DeclarativeBase` and use `Mapped[...]` and `mapped_column()` annotations.
- **Formatting & Linting:** Code is formatted with **Black** (line length 100) and linted with **Ruff**.
- **Docstrings:** Use Google-style docstrings for non-trivial services and quantum algorithms.

---

## 2. TypeScript & React Standards (`frontend/`)

- **Strict TypeScript:** `strict: true` in `tsconfig.json`. Explicitly avoid `any`; use `unknown` with type guards where necessary.
- **Functional Components:** All components must be written as functional components with explicit props interfaces:
  ```typescript
  interface ButtonProps {
    variant?: 'primary' | 'secondary' | 'danger';
    isLoading?: boolean;
    onClick?: () => void;
    children: React.ReactNode;
  }
  ```
- **State Partitioning:**
  - Server state: TanStack Query (`useQuery`, `useMutation`).
  - Client state: Zustand (`usePlayerStore`).
  - Component state: React `useState` / `useRef`.
- **Styling:** Use utility-first Tailwind CSS. Do not write arbitrary inline `style={{ ... }}` objects unless calculating dynamic continuous values (e.g. audio scrubber width percentage).

---

## 3. Naming Conventions

| Entity | Python (Backend) | TypeScript (Frontend) | Example |
| :--- | :--- | :--- | :--- |
| **Files & Modules** | `snake_case.py` | `kebab-case.ts` or `PascalCase.tsx` | `tts_service.py`, `AudioPlayer.tsx` |
| **Classes & Models** | `PascalCase` | `PascalCase` | `SpeechGeneration`, `TTSRequest` |
| **Functions & Methods**| `snake_case()` | `camelCase()` | `synthesize_speech()`, `formatDuration()` |
| **Constants** | `UPPER_SNAKE_CASE` | `UPPER_SNAKE_CASE` | `TTS_LIMITS`, `MAX_QUBITS` |
| **Interfaces / Types** | `PascalCase` | `PascalCase` | `Voice`, `HistoryFilterParams` |
