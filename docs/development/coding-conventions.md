# Bloop Development — Coding Conventions & Standards

## 1. Python Code Standards (PEP 8 & Clean Code)

### 1.1 Formatting & Typing
- **Type Hints:** All public functions, method arguments, and return types must include explicit type hints.
  ```python
  def synthesize_speech(
      text: str,
      voice_id: str,
      options: Optional[Dict[str, Any]] = None
  ) -> bytes:
      ...
  ```
- **Docstrings:** Use Google-style or standard Python docstrings for classes and non-trivial functions.
- **Async Usage:** Use `async def` only when performing non-blocking I/O (e.g. streaming audio chunks, HTTP requests). Use synchronous `def` for pure CPU operations.

### 1.2 Python Naming Rules
- **Modules / Files:** `snake_case.py` (e.g., `user_repository.py`, `speech_service.py`)
- **Classes:** `PascalCase` (e.g., `VoiceService`, `ElevenLabsProvider`)
- **Functions & Methods:** `snake_case()` (e.g., `get_by_id()`, `generate_speech()`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `DEFAULT_PAGE_SIZE`, `MAX_TEXT_LENGTH`)
- **Pydantic Schemas:** `PascalCase` with suffix `Request` or `Response` (e.g., `TTSRequest`, `TTSResponse`)

---

## 2. TypeScript & React Code Standards

### 2.1 Strict Types & No `any`
- **Zero `any` Policy:** Explicitly define interfaces or use `unknown` with type guards.
- **Functional Components:** Use arrow functions or `React.FC<Props>` with typed props.
- **Avoid Enormous Components:** Split components exceeding 200 lines into focused sub-components.

### 2.2 TypeScript / React Naming Rules
- **Components:** `PascalCase.tsx` (e.g., `Button.tsx`, `AudioPlayer.tsx`, `WorkspacePage.tsx`)
- **Custom Hooks:** `useCamelCase.ts` (e.g., `useDebounce.ts`, `useGenerateSpeech.ts`)
- **Utilities:** `camelCase.ts` (e.g., `formatters.ts`, `validation.ts`)
- **Type Definition Files:** `feature.types.ts` or `index.ts` within feature directories
- **Test Files:** `<Subject>.test.tsx` or `<subject>.test.ts` (e.g., `Button.test.tsx`, `validation.test.ts`)

---

## 3. Database Naming Conventions (PostgreSQL)

- **Tables:** Plural `snake_case` (e.g., `users`, `voices`, `speech_generations`, `favorites`)
- **Columns:** `snake_case` (e.g., `user_id`, `created_at`, `audio_url`, `character_count`)
- **Primary Keys:** `id` (integer auto-incrementing or UUID string)
- **Foreign Keys:** `<singular_target_table>_id` (e.g., `user_id`, `voice_id`)
- **Timestamps:** Always include `created_at` (and `updated_at` where mutable) with UTC defaults.

---

## 4. REST API Endpoint Naming Conventions

- **Prefix:** `/api/v1/`
- **Resources:** Plural, lowercase nouns with kebab-case for multi-word subresources:
  - `GET /api/v1/voices`
  - `POST /api/v1/tts`
  - `GET /api/v1/history`
  - `GET /api/v1/quantum/circuits`
- **Machine-Readable Response Contract:**
  - Success: `{"success": true, "data": { ... }}`
  - Error: `{"success": false, "error": {"code": "ERROR_CODE", "message": "..."}}`
