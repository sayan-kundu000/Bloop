# Audio Download Pipeline Architecture

This document describes the mechanics, security model, content headers, and browser download workflow for the **Bloop** audio delivery subsystem.

---

## 1. Overview

The Bloop download pipeline enables authenticated users to retrieve generated audio files directly as attachments to their local device without interrupting current audio playback or redirecting the browser window.

```mermaid
flowchart TD
    A[User Clicks Download] --> B[Browser Issues GET Request]
    B --> C[GET /api/v1/tts/{generation_id}/download]
    C --> D[Bearer Token Verification]
    D --> E[SpeechGeneration Database Lookup]
    E --> F[Ownership Authorization Check]
    F --> G{User Owns Asset?}
    G -->|No| H[HTTP 403 Forbidden]
    G -->|Yes| I[Locate Temporary File on Server Disk]
    I --> J{File Exists?}
    J -->|No| K[HTTP 404 AUDIO_NOT_FOUND]
    J -->|Yes| L[Set Attachment Content Headers]
    L --> M[Stream Binary File to Client]
    M --> N[Browser Native Save File Dialog]
```

---

## 2. API Endpoints

### Supported Download Routes:
- `GET /api/v1/tts/{generation_id}/download` (Preferred versioned ID route)
- `GET /api/v1/tts/download/{identifier}` (Filename / legacy compatibility route)

---

## 3. HTTP Header Standards

The download endpoint configures response headers to instruct the client browser to treat the incoming payload as a file download rather than inline media:

```http
HTTP/1.1 200 OK
Content-Type: audio/mpeg
Content-Disposition: attachment; filename="bloop-speech-42.mp3"
Content-Length: 524288
Accept-Ranges: bytes
Cache-Control: private, no-cache
```

### Deterministic Filename Formatting:
- Filenames follow the deterministic format: `bloop-speech-{generation_id}.{format}` (e.g., `bloop-speech-42.mp3` or `bloop-speech-42.wav`).
- User-supplied text strings are **never** used to construct downloadable filenames, preventing injection of malicious characters, null bytes, or navigation symbols.

---

## 4. Security & Access Boundaries

1. **Strict Ownership Validation**:
   - Audio generations are bound to the `user_id` of the author.
   - Non-owners receive `HTTP 403 Forbidden` (`GENERATION_ACCESS_DENIED`).
2. **Path Traversal Mitigation**:
   - Filenames are extracted strictly using `os.path.basename` and verified to reside inside `settings.AUDIO_STORAGE_PATH`.
   - Any query containing directory traversal tokens (`../`, `..%2F`) is safely stripped or rejected with `HTTP 404`.
3. **No Direct External Provider Exposure**:
   - The React browser client never makes requests directly to ElevenLabs or any external API.
   - All downloads flow through the authenticated Bloop backend gateway.
