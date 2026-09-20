# ADR-023: Bloop Audio Player, Media Delivery & Download Architecture

## Status
Accepted

## Context
Following the implementation of speech generation (Prompt 19), Bloop requires a dedicated, accessible, and browser-compatible audio presentation and download layer. The audio player must consume the synthesized speech result (`TTSResponse`), provide responsive playback controls, live progress tracking, volume modulation with mute/unmute restoration, and authenticated file downloads across modern web browsers (Chrome, Firefox, Safari, Edge, mobile/desktop).

## Decision Drivers
1. **Security & Provider Isolation**: The browser must never communicate directly with ElevenLabs or expose third-party credentials. All audio streams and downloads flow through the authenticated FastAPI backend.
2. **Standard Native Media**: Avoid heavyweight third-party audio player dependencies (e.g. Howler, WaveSurfer) in favor of the standardized HTML5 `<audio>` element and `HTMLAudioElement` DOM API.
3. **Robust Lifecycle & Resource Cleanup**: Prevent phantom audio playback, duplicate audio elements, and browser memory leaks caused by lingering event listeners or unrevoked Object URLs.
4. **Resilient Error Taxonomy**: Explicitly decouple TTS generation errors from audio playback errors and file download errors.
5. **Accessibility (WCAG 2.1 AA)**: Provide semantic controls, keyboard navigation (Tab, Space, Enter, Range arrows), clear ARIA roles/live regions, and minimum 44px touch targets.

## Architectural Decisions

### 1. Native HTML5 Audio with `useAudioPlayer` Hook
Instead of relying on large external audio frameworks or unmanaged DOM elements, audio lifecycle is encapsulated in `useAudioPlayer`. This custom hook instantiates and controls an internal `HTMLAudioElement`, synchronizing React state through native media events (`loadedmetadata`, `play`, `pause`, `waiting`, `playing`, `timeupdate`, `progress`, `ended`, `error`).

```mermaid
flowchart TD
    A[TTSResponse / AudioSource] --> B[AudioPlayer Component]
    B --> C[useAudioPlayer Hook]
    C --> D[HTMLAudioElement]
    D -- Events: play/pause/timeupdate/waiting/error --> C
    C --> E[AudioControls: Play / Pause / Replay]
    C --> F[AudioProgress: Scrubber & Live Duration]
    C --> G[VolumeControl: Slider & Mute Toggle]
    C --> H[AudioStatus: Buffering & Playback Retry]
    B --> I[AudioDownloadButton]
    I --> J[audioService.downloadAudio]
    J --> K[FastAPI: GET /api/v1/tts/download/{id}]
```

### 2. Event-Driven Playback Lifecycle
The player executes a deterministic state machine:
- `idle`: No audio loaded or empty workspace.
- `loading`: Source changed; media metadata loading via `audio.load()`.
- `ready`: Metadata loaded; duration resolved; awaiting user-initiated play.
- `playing`: Active playback; real-time elapsed position via `timeupdate`.
- `buffering`: Network buffer stall indicated via `waiting` event.
- `paused`: User or system paused.
- `ended`: Playback finished; transforms control into Replay action.
- `error`: Source unavailable or network drop; presents retry action without forcing speech re-generation.

### 3. Audio Delivery & Download Boundary
- **Audio Streaming**: Consumes `GET /api/v1/tts/audio/{identifier}` which supports RFC 7233 byte-range streaming.
- **Direct Download**: Handled by `audioService.downloadAudio()` via authenticated `apiClient` (`responseType: 'blob'`). It creates a temporary `URL.createObjectURL(blob)`, sets a sanitized filename (e.g., `bloop-voice-name-42.mp3`), programmatically triggers the download, and cleans up the Object URL via `URL.revokeObjectURL()` to prevent memory leaks.
- **Fallback**: If blob construction fails due to browser sandbox restrictions, it degrades gracefully to a direct authenticated anchor trigger.

### 4. Filename Sanitization & MIME Resolution
To prevent path traversal (`../../`) or executable file spoofing, `sanitizeFilename()` strips illegal characters (`<>:"/\\|?*`), collapses spaces to hyphens, truncates the stem to 60 characters, and matches extension via `resolveMimeExtension()`.

### 5. Why Local State over Global State
A single generated result belongs to the active workspace session. Storing full playback state in global stores (e.g. Zustand) risks orphan audio elements continuing to play in background threads. Component-local lifecycle in `useAudioPlayer` guarantees that unmounting or synthesizing new speech automatically pauses previous playback, detaches listeners, and reclaims memory.

### 6. Why No Raw Audio Blobs in PostgreSQL
Audio binary blobs are strictly stored in designated media storage (local filesystem / object store) rather than PostgreSQL bytea columns. PostgreSQL stores only metadata (`audio_url`, `download_url`, `audio_filename`, `duration_seconds`, `audio_format`, `content_type`), preserving database performance, transaction log efficiency, and seamless HTTP Range streaming.

## Consequences
- **Positive**: Zero external audio dependencies; full memory safety; seamless mobile/desktop responsiveness; strict separation between generation and playback failures.
- **Negative**: HTML5 Audio autoplay policies require user gesture; handled by adhering to user-initiated playback by default.
