# ADR-016: Speech Generation API, Audio Processing, and Controlled Audio Delivery Pipeline

## Status
Accepted

## Context
Bloop requires a full-stack text-to-speech pipeline capable of orchestrating input validation, dynamic voice resolution, ElevenLabs synthesis, binary audio validation, disk buffering, metadata persistence in PostgreSQL, browser audio streaming with seeking support, and direct file downloads.

Key architectural constraints include:
1. **Dynamic Voice Invariant**: Strict prohibition against hardcoding actual ElevenLabs production voice IDs or catalog lists into application code, database migrations, or schemas.
2. **Ephemeral Disk Environment (Render)**: The backend runs on containerized services with ephemeral filesystems; database bloat from storing large binary files in PostgreSQL must be avoided.
3. **Player Interactivity**: The React audio player must support play, pause, seek (RFC 7233 Range requests), and volume control.
4. **Security & Ownership**: Audio assets must be strictly protected against unauthorized access, cross-user data leaks, and directory traversal.
5. **Separation of Concerns**: Thin routing layer, modular `SpeechService`, dedicated `AudioProcessor`, and decoupled `AudioDeliveryService`.

## Decision

1. **Service Architecture**:
   - **`SpeechService`**: Orchestrates authoritative validation, provider dispatch, audio normalization, database persistence, and failure auditing.
   - **`AudioProcessor`**: Validates binary payloads (length boundaries, magic bytes, rejecting text/HTML error responses) and formats metadata without decoding or re-encoding raw bytes.
   - **`AudioDeliveryService`**: Handles temporary local filesystem storage, UUID filename generation, RFC 7233 partial content streaming (HTTP 206), attachment download headers, and lifecycle cleanup.

2. **Storage Separation**:
   - PostgreSQL stores lightweight generation metadata (`SpeechGeneration`).
   - Server storage buffers raw audio files temporarily (`backend/app/storage/audio/{uuid}.mp3`).
   - Automated retention cleanup prunes assets older than 24 hours.

3. **Controlled Delivery & Access Control**:
   - Audio delivery routes enforce ownership checks. Non-owners receive HTTP 403 `GENERATION_ACCESS_DENIED`.
   - Dual-route resolution supports both generation ID (`/api/v1/tts/{generation_id}/audio`) and legacy filename paths (`/api/v1/tts/audio/{filename}`).
   - Path traversal is prevented via strict `os.path.basename` extraction and directory containment checks.

4. **Failure Consistency**:
   - If synthesis or audio validation fails, a `SpeechGeneration` audit record with `status="failed"` is persisted before propagating domain errors.
   - If database persistence fails after audio buffering, the temporary file is immediately pruned from disk to prevent storage accumulation.

## Consequences

### Positive
- **Zero Database Bloat**: PostgreSQL remains fast and lean by storing only metadata.
- **Rich User Experience**: RFC 7233 Range support enables instant scrubbing and seeking in HTML5/React audio players.
- **Render & Vercel Readiness**: Works seamlessly with stateless backend containers and detached React frontends.
- **Clean Security Boundaries**: User audio assets cannot be accessed across account boundaries.
- **Provider Isolation**: ElevenLabs API keys and proprietary objects are completely isolated within backend adapters.

### Trade-offs & Mitigations
- *Ephemeral Storage on Render*: Stored audio may be purged upon server restarts.
  - *Mitigation*: The `AudioDeliveryService` abstraction is structured so that a cloud object storage driver (e.g. S3 / Cloudflare R2) can be introduced in a future phase without modifying routers or player interfaces.
