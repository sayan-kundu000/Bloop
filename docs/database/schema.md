# Bloop Database Relational Schema Specification

**Document Identifier:** BLOOP-DB-SCHEMA-007  
**Status:** Approved Technical Standard  
**Target Engine:** PostgreSQL 16 (Render Managed)  

---

## 1. Schema Tables Overview

The Bloop relational schema consists of 7 normalized tables:

| Table Name | Primary Key | Foreign Keys | Purpose |
| :--- | :--- | :--- | :--- |
| `users` | `id` (SERIAL / INT) | None | Core user identity, hashed credentials, and lifecycle status. |
| `user_preferences` | `id` (SERIAL / INT) | `user_id` (users.id), `default_language_code` (languages.code) | User UI settings, playback speed, and default speech parameters. |
| `languages` | `code` (VARCHAR(10))| None | Standard ISO language and locale catalog metadata. |
| `voices` | `id` (SERIAL / INT) | `language_code` (languages.code) | Dynamic voice registration registry (no hardcoded voice records). |
| `speech_generations` | `id` (SERIAL / INT) | `user_id` (users.id) | Generated speech metadata, duration, audio file reference, status. |
| `favorites` | `id` (SERIAL / INT) | `user_id` (users.id), `generation_id` (speech_generations.id) | Saved speech generations per user with uniqueness constraint. |
| `quantum_experiments`| `id` (SERIAL / INT) | `user_id` (users.id) | Quantum circuit logs, payloads, results JSON, and benchmark runs. |

---

## 2. Table Specifications

### 2.1 `users` Table
Stores user credentials and account states.

| Column | Type | Nullable | Default | Constraints / Index | Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `id` | `INTEGER` | No | Auto (SERIAL) | `PRIMARY KEY`, Index | Surrogate identifier. |
| `email` | `VARCHAR(255)`| No | None | `UNIQUE`, Index | Normalized lowercase user email address. |
| `hashed_password`| `VARCHAR(255)`| No | None | None | Bcrypt hashed password string. Never plaintext. |
| `full_name` | `VARCHAR(100)`| Yes | `NULL` | None | User display name. |
| `is_active` | `BOOLEAN` | No | `TRUE` | None | Active account status flag. |
| `is_superuser` | `BOOLEAN` | No | `FALSE` | None | Administrative privileges flag. |
| `created_at` | `TIMESTAMPTZ` | No | `now() UTC` | None | Account creation timestamp. |
| `updated_at` | `TIMESTAMPTZ` | No | `now() UTC` | None | Last modification timestamp. |

---

### 2.2 `user_preferences` Table
Maintains personalized settings for each registered user.

| Column | Type | Nullable | Default | Constraints / Index | Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `id` | `INTEGER` | No | Auto (SERIAL) | `PRIMARY KEY`, Index | Surrogate identifier. |
| `user_id` | `INTEGER` | No | None | `UNIQUE`, FK `users.id` (CASCADE) | 1-to-1 relationship with `users`. |
| `default_language_code`| `VARCHAR(10)` | Yes | `NULL` | FK `languages.code` (SET NULL) | Preferred synthesis language. |
| `default_voice_id` | `VARCHAR(100)` | Yes | `NULL` | None | Preferred dynamic voice ID. |
| `theme` | `VARCHAR(20)` | No | `'dark'` | None | UI theme mode (`dark`, `light`, `system`). |
| `audio_speed` | `FLOAT` | No | `1.0` | None | Default speech playback speed multiplier. |
| `auto_play` | `BOOLEAN` | No | `TRUE` | None | Automatically play generated audio. |
| `created_at` | `TIMESTAMPTZ` | No | `now() UTC` | None | Preference record creation time. |
| `updated_at` | `TIMESTAMPTZ` | No | `now() UTC` | None | Preference last update time. |

---

### 2.3 `languages` Table
Defines ISO language and regional dialect codes.

| Column | Type | Nullable | Default | Constraints / Index | Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `code` | `VARCHAR(10)` | No | None | `PRIMARY KEY`, Index | Standard BCP-47 language tag (e.g. `en-US`, `es-ES`). |
| `name` | `VARCHAR(100)`| No | None | None | English descriptive name (e.g. `English (US)`). |
| `native_name` | `VARCHAR(100)`| Yes | `NULL` | None | Endonym representation (e.g. `Français`, `हिन्दी`). |
| `is_active` | `BOOLEAN` | No | `TRUE` | None | Flag indicating language is enabled. |
| `created_at` | `TIMESTAMPTZ` | No | `now() UTC` | None | Record insertion timestamp. |

---

### 2.4 `voices` Table
Dynamic voice registry for user-injected and external provider voices.
> **ZERO VOICES INVARIANT:** Production migrations and initial schemas insert zero records into this table.

| Column | Type | Nullable | Default | Constraints / Index | Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `id` | `INTEGER` | No | Auto (SERIAL) | `PRIMARY KEY`, Index | Surrogate internal identifier. |
| `voice_id` | `VARCHAR(100)`| No | None | `UNIQUE`, Index | External provider ID or dynamic registry key. |
| `name` | `VARCHAR(100)`| No | None | None | Display name of the voice. |
| `language_code` | `VARCHAR(10)` | No | None | FK `languages.code` (CASCADE), Index | Associated ISO language code. |
| `gender` | `VARCHAR(20)` | No | `'unspecified'`| None | Vocal gender (`female`, `male`, `neutral`). |
| `accent` | `VARCHAR(50)` | Yes | `NULL` | None | Regional accent descriptor (e.g. `American`, `British`). |
| `description` | `VARCHAR(255)`| Yes | `NULL` | None | Character/tone summary. |
| `provider` | `VARCHAR(50)` | No | `'dynamic'` | None | Provider origin (`elevenlabs`, `simulation`, `custom`). |
| `preview_url` | `VARCHAR(255)`| Yes | `NULL` | None | Optional URL to preview audio sample. |
| `is_active` | `BOOLEAN` | No | `TRUE` | None | Availability flag. |
| `is_user_configured`| `BOOLEAN` | No | `FALSE` | None | True if voice was registered by an end-user. |
| `created_at` | `TIMESTAMPTZ` | No | `now() UTC` | None | Registration timestamp. |
| `updated_at` | `TIMESTAMPTZ` | No | `now() UTC` | None | Last update timestamp. |

---

### 2.5 `speech_generations` Table
Core speech synthesis request and result metadata.
> **NO AUDIO BINARY INVARIANT:** Exclusively references filenames on disk; audio binary waveforms are never persisted in rows.

| Column | Type | Nullable | Default | Constraints / Index | Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `id` | `INTEGER` | No | Auto (SERIAL) | `PRIMARY KEY`, Index | Generation primary key. |
| `user_id` | `INTEGER` | Yes | `NULL` | FK `users.id` (SET NULL), Index | Owning user (null for anonymous). |
| `text` | `TEXT` | No | None | None | Text prompt synthesized into speech. |
| `char_count` | `INTEGER` | No | None | None | Character count of input text. |
| `word_count` | `INTEGER` | No | None | None | Word count of input text. |
| `language_code` | `VARCHAR(10)` | No | None | None | Language code used for synthesis. |
| `voice_id` | `VARCHAR(100)`| No | None | None | Voice ID used for synthesis. |
| `voice_name` | `VARCHAR(100)`| Yes | `NULL` | None | Snapshot of voice display name. |
| `status` | `VARCHAR(20)` | No | `'completed'`| Index | Lifecycle: `pending`, `processing`, `completed`, `failed`. |
| `audio_filename`| `VARCHAR(255)`| No | None | `UNIQUE`, Index | Disk filename (e.g. `bloop_123_456.mp3`). |
| `duration_seconds`| `FLOAT` | Yes | `0.0` | None | Audio duration in seconds. |
| `file_size_bytes`| `INTEGER` | Yes | `0` | None | File size on storage in bytes. |
| `audio_format` | `VARCHAR(10)` | No | `'mp3'` | None | Audio codec format (`mp3`, `wav`). |
| `provider` | `VARCHAR(50)` | No | `'elevenlabs'`| None | Synthesis provider engine. |
| `provider_request_id`| `VARCHAR(100)`| Yes | `NULL` | None | Vendor request ID for diagnostics. |
| `error_code` | `VARCHAR(50)` | Yes | `NULL` | None | Error classification code if failed. |
| `error_message` | `TEXT` | Yes | `NULL` | None | Sanitized failure message (no secrets). |
| `created_at` | `TIMESTAMPTZ` | No | `now() UTC` | Index | Synthesis timestamp. |
| `updated_at` | `TIMESTAMPTZ` | No | `now() UTC` | None | Status update timestamp. |

**Composite Indexes:**
- `ix_speech_generations_user_created` on `(user_id, created_at)`: Powers paginated history queries.

---

### 2.6 `favorites` Table
User bookmarks for generated speech audio.

| Column | Type | Nullable | Default | Constraints / Index | Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `id` | `INTEGER` | No | Auto (SERIAL) | `PRIMARY KEY`, Index | Surrogate identifier. |
| `user_id` | `INTEGER` | No | None | FK `users.id` (CASCADE), Index | User who saved the bookmark. |
| `generation_id` | `INTEGER` | No | None | FK `speech_generations.id` (CASCADE), Index | Bookmarked generation reference. |
| `label` | `VARCHAR(100)`| Yes | `NULL` | None | User-defined custom tag or bookmark title. |
| `created_at` | `TIMESTAMPTZ` | No | `now() UTC` | None | Timestamp when favorited. |

**Unique Constraints:**
- `uq_user_generation_favorite` on `(user_id, generation_id)`: Prevents duplicate bookmarks.

---

### 2.7 `quantum_experiments` Table
Logs quantum intelligence executions and circuit simulations.

| Column | Type | Nullable | Default | Constraints / Index | Description |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `id` | `INTEGER` | No | Auto (SERIAL) | `PRIMARY KEY`, Index | Surrogate identifier. |
| `user_id` | `INTEGER` | Yes | `NULL` | FK `users.id` (SET NULL), Index | Owning user (optional). |
| `experiment_type`| `VARCHAR(50)` | No | None | Index | `text`, `emotion`, `semantic`, `circuit`, `benchmark`. |
| `title` | `VARCHAR(200)`| No | None | None | Experiment display title. |
| `description` | `TEXT` | Yes | `NULL` | None | Optional experiment hypothesis/notes. |
| `status` | `VARCHAR(20)` | No | `'completed'`| Index | Lifecycle: `pending`, `processing`, `completed`, `failed`. |
| `input_payload` | `JSON` / `JSONB`| No | None | None | Quantum parameters, prompt, and gate list. |
| `results` | `JSON` / `JSONB`| No | None | None | Probabilities, state vectors, counts dict. |
| `qubit_count` | `INTEGER` | Yes | `2` | None | Qubit register size. |
| `circuit_depth` | `INTEGER` | Yes | `0` | None | Circuit gate depth. |
| `execution_time_ms`| `FLOAT` | Yes | `0.0` | None | Simulation execution time in milliseconds. |
| `simulator` | `VARCHAR(50)` | Yes | `'qiskit_aer'`| None | Simulator engine (`qiskit_aer`, `pennylane_default_qubit`). |
| `error_code` | `VARCHAR(50)` | Yes | `NULL` | None | Diagnostic error code if failed. |
| `created_at` | `TIMESTAMPTZ` | No | `now() UTC` | Index | Execution timestamp. |
| `updated_at` | `TIMESTAMPTZ` | No | `now() UTC` | None | Last update timestamp. |

**Composite Indexes:**
- `ix_quantum_experiments_user_created` on `(user_id, created_at)`: Supports user-scoped historical experiment queries.
