# Bloop Backend Architecture — Dynamic Voice Architecture & Isolation

## 1. Overview

Bloop's **Dynamic Voice Architecture** allows speech voices to be configured, registered, and discovered dynamically at runtime without modifying source code, altering database migrations, or hardcoding third-party vendor IDs.

```mermaid
flowchart LR
    A[PostgreSQL / Configuration]
    B[Voice Registry]
    C[Voice API]
    D[React]
    E[Language Selection]
    F[Compatible Voices]
    G[TTS Request]

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
```

---

## 2. Critical Architectural Principles

### 2.1 Provider Voice ID Abstraction
To prevent tight vendor coupling and protect internal vendor identifiers:
- **`voice_id` (Public):** The application-level identifier exposed to clients and stored in frontend state (e.g. `voice-serena-natural`).
- **`provider_voice_id` (Internal):** The actual provider-specific ID (e.g. ElevenLabs ID `21m00Tcm4TlvDq8ikWAM`). It is stored securely in the database and **strictly never exposed** through `/api/v1/voices` or public API schemas.

### 2.2 Zero Hardcoded Production Voices
The production database starts with an empty voice catalog:
- Actual voices added: **NO**
- Actual voice IDs added: **NO**
- Fake voices added: **NO**
- Dynamic voice architecture: **READY**

Voices are populated dynamically through user-provided configuration files (`backend/voices_config.json`), administrative dynamic registration (`POST /api/v1/voices`), or dynamic sync routines.

---

## 3. Voice Domain Model

The `Voice` model (`backend/app/models/voice.py`) maintains:

| Field | Type | Visibility | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | Public | Primary key |
| `voice_id` | `VARCHAR(100)` | Public | Unique application voice identifier |
| `provider_voice_id` | `VARCHAR(100)` | **Internal Only** | Raw vendor ID (e.g., ElevenLabs ID); masked from API responses |
| `name` | `VARCHAR(100)` | Public | Display name |
| `language_code` | `VARCHAR(10)` | Public | Primary language code |
| `gender` | `VARCHAR(20)` | Public | Gender descriptor (`female`, `male`, `neutral`, `unspecified`) |
| `accent` | `VARCHAR(50)` | Public | Regional accent |
| `description` | `VARCHAR(255)` | Public | Qualitative characteristics summary |
| `provider` | `VARCHAR(50)` | Public | Provider identifier (`elevenlabs`, `dynamic`, `simulation`) |
| `preview_url` | `VARCHAR(255)` | Public | Audio preview URL |
| `is_active` | `BOOLEAN` | Public | Active state flag |
| `is_user_configured` | `BOOLEAN` | Public | True if user/custom registered |
| `metadata` | `JSON` | Public/Optional | Extensible style and acoustic flags |

---

## 4. Empty Catalog Graceful Degradation

If no voices are registered:
- `GET /api/v1/voices` returns `200 OK` with `{"success": true, "data": []}`.
- The UI handles the empty state gracefully with a prompt notifying the user to configure or select available voices.
- `POST /api/v1/tts` cleanly rejects with `422 Unprocessable Entity` and error code `INVALID_VOICE`.
