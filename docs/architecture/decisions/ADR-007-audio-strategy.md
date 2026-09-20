# ADR-007: Temporary Server Storage with HTTP 206 Streaming vs Database Binary Blobs

## Status
**Accepted**

## Context
Speech synthesis generates binary MPEG-3 (MP3) audio files ranging from 20 KB (short phrases) to 2 MB (long paragraphs). We evaluated strategies for storing, retrieving, and delivering these audio payloads to client browsers.

Alternatives considered:
1. **Database BLOB Storage:** Storing raw audio binary bytes directly in PostgreSQL `BYTEA` columns alongside speech generation metadata.
2. **External Object Storage (AWS S3 / Cloudflare R2):** Storing files in S3 buckets and generating pre-signed URLs.
3. **Local Server Disk Storage with HTTP 206 Range Streaming:** Storing generated files in a dedicated server-side directory (`backend/app/storage/audio/`), recording only the relative filename/URI in PostgreSQL, and streaming via HTTP 206 Partial Content byte ranges.

## Decision
Adopt **Local Server Storage with HTTP 206 Partial Content Streaming**:
1. Binary audio files are stored in `backend/app/storage/audio/` using deterministic, collision-resistant UUID filenames (`bloop-{uuid4}.mp3`).
2. PostgreSQL stores only metadata: character count, duration, voice, provider, and `audio_filename`. No binary audio data is stored in the database.
3. The audio endpoint (`GET /api/v1/tts/audio/{filename}`) supports standard HTTP `Range` headers (`bytes=start-end`), responding with `HTTP 206 Partial Content`.
4. A dedicated download endpoint (`GET /api/v1/tts/download/{filename}`) serves files with `Content-Disposition: attachment`.
5. An automated cleanup routine removes orphaned or expired audio files older than 24 hours.

## Rationale
1. **Database Health & Performance:** Storing large binary BLOBs degrades PostgreSQL cache efficiency, balloons database backups, increases connection memory, and hurts table scan latencies.
2. **Instant Audio Scrubbing & Playback:** Native HTTP 206 Range streaming allows the browser's `<audio>` tag to jump to arbitrary timestamps, scrub smoothly, and begin playback within milliseconds without downloading the entire file upfront.
3. **Intermediate-Level Simplicity:** Avoids external AWS S3 / Cloudflare credentials, IAM policies, and cloud egress billing, keeping the architecture self-contained on Render.
4. **Future Object Storage Readiness:** Because the database stores only the filename/key, migrating to S3 or R2 in the future requires changing only the storage service adapter, without database schema modifications.

## Consequences
### Positive
- PostgreSQL database remains lean, fast, and focused purely on relational metadata.
- Low-latency seeking and instant audio playback in the frontend UI.
- No third-party cloud storage dependencies or credentials required for intermediate deployment.

### Negative / Trade-offs
- Render ephemeral disk storage: on free-tier Render restarts, local disk files are reset (acceptable for ephemeral audio generation in development and demo environments). Production deployments can attach a persistent Render disk to `backend/app/storage/audio/`.
