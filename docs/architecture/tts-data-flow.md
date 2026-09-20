# Bloop — Text-to-Speech (TTS) Data Flow Specification

**Document Identifier:** BLOOP-TTS-DATAFLOW-V1  
**Project:** Bloop — AI Text-to-Speech & Quantum Intelligence Platform  
**Target Milestone:** Intermediate-Level TTS Integration Architecture  
**Status:** Approved Technical Design  
**Authority:** Bloop Master Prompt & Prompt 02  

---

## 1. Overview & Source Foundation

This document details the complete end-to-end data flow for speech synthesis in Bloop. The architecture mirrors the core responsibilities established in the foundational specification:
- User submits text, language, and voice via React frontend.
- FastAPI backend receives, validates, and authenticates the request.
- Backend resolves dynamic voice metadata and verifies language compatibility.
- Backend communicates with ElevenLabs over secure HTTPS (or invokes offline simulation fallback).
- Binary audio data is written to server storage and indexed in PostgreSQL.
- Streamable audio URLs are returned to the client, unlocking playback and download.

---

## 2. The 21-Step Canonical TTS Execution Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant UI as React Frontend (Workspace)
    participant Router as FastAPI Router (/api/v1/tts)
    participant Auth as Auth Dependency (get_current_user)
    participant Pydantic as Pydantic v2 Validation
    participant Service as TTSService
    participant VoiceRepo as VoiceRepository
    participant Provider as ElevenLabsProvider / SimulationProvider
    participant ElevenLabs as ElevenLabs Cloud API
    participant Storage as AudioManager (Disk Storage)
    participant GenRepo as SpeechGenerationRepository
    participant DB as PostgreSQL Database
    participant Player as AudioPlayerBar (Frontend)

    User->>UI: 1. Types text in workspace
    UI->>UI: 2. Computes live character count, word count, estimated duration
    User->>UI: 3. Selects language (e.g., en-US)
    User->>UI: 4. Selects voice (e.g., Sarah)
    User->>UI: 5. Clicks "Generate Speech"
    UI->>UI: 6. Client validation (1 <= len <= 2,500, non-empty)
    UI->>Router: 7. POST /api/v1/tts (Bearer JWT, JSON payload)
    Router->>Auth: 8. Verify JWT Bearer token signature & user status
    Auth-->>Router: Authenticated User instance
    Router->>Pydantic: 9. Validate schema structure and types
    Router->>Service: 10. synthesize_speech(user_id, request)
    Service->>Service: 11. Authoritative text boundary check (1 to 2,500 chars)
    Service->>VoiceRepo: 12. get_voice(request.voice_id)
    VoiceRepo->>DB: Query voice entity & language compatibility
    DB-->>VoiceRepo: Voice Entity
    VoiceRepo-->>Service: Validated Voice record
    Service->>Provider: 13. synthesize(text, voice_id, options)
    
    alt ElevenLabs Configured (API Key Present)
        Provider->>ElevenLabs: 14. POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}
        ElevenLabs-->>Provider: 15. Binary MP3 Audio Bytes (200 OK)
    else Simulation Mode (API Key Missing / Offline)
        Provider->>Provider: 14. Generate synthetic sinusoidal waveform bytes
    end
    
    Provider-->>Service: 16. Audio Bytes Returned
    Service->>Storage: 17. write_audio_file(audio_bytes)
    Storage-->>Service: Saved filename: "bloop-{uuid4}.mp3"
    Service->>GenRepo: 18. record_generation(user_id, text, voice, filename, duration)
    GenRepo->>DB: INSERT INTO speech_generations (...) VALUES (...)
    DB-->>GenRepo: Persisted Record (id: 42)
    GenRepo-->>Service: Generation Entity
    Service-->>Router: 19. TTSResponse (id, audio_url, download_url, metrics)
    Router-->>UI: 20. HTTP 200 { success: true, data: { ... } }
    UI->>Player: 21. Load audio stream into AudioPlayerBar; playback & download ready
```

---

## 3. Dual-Layer Validation Flow

To prevent unnecessary network calls, cost overruns, and database corruption, input validation is enforced at both client and server perimeters:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            DUAL-LAYER VALIDATION                            │
├──────────────────────────┬──────────────────────────────────────────────────┤
│ Layer 1: Frontend        │ * Live character counter updates on every keystroke.│
│ (Client UX Perimeter)    │ * Generate button disabled if text is empty.     │
│                          │ * Input blocked if character length exceeds 2,500│
│                          │ * Voice dropdown requires an active selection.   │
├──────────────────────────┼──────────────────────────────────────────────────┤
│ Layer 2: Backend         │ * Pydantic v2 rejects missing fields or bad types│
│ (Authoritative Security) │ * Server trims whitespace; verifies 1 <= len <=  │
│                          │   2,500 characters.                              │
│                          │ * Voice existence verified against database.     │
│                          │ * Voice language compatibility strictly checked. │
└──────────────────────────┴──────────────────────────────────────────────────┘
```

---

## 4. ElevenLabs Provider Boundary & Credential Protection

The system guarantees that third-party credentials never leak to the client:
1. **Zero Client Secret Exposure:** The React client never handles `ELEVENLABS_API_KEY`. The frontend passes only abstract voice IDs and text strings to `/api/v1/tts`.
2. **Server-Side HTTPX Client:** `ElevenLabsProvider` manages an asynchronous `httpx.AsyncClient` with connection pooling, keeping credentials strictly in server memory.
3. **Provider Error Normalization:**
   - ElevenLabs HTTP 401: Normalized to `PROVIDER_AUTH_ERROR`.
   - ElevenLabs HTTP 429: Normalized to `PROVIDER_QUOTA_EXCEEDED`.
   - Network Timeout (> 30s): Normalized to `PROVIDER_TIMEOUT_ERROR`.
   - No stack traces or vendor-specific tokens are leaked in API error responses.

---

## 5. Audio Storage & HTTP 206 Partial Content Streaming

```
Browser <audio> Tag
        │
        ▼ (1) GET /api/v1/tts/audio/bloop-abc123.mp3
        │     Header: Range: bytes=0-1048575
        │
FastAPI Streaming Route (/storage/audio_manager.py)
        │
        ▼ (2) Reads file size, parses start/end byte offsets
        │     Opens binary file in read mode
        │
        ▼ (3) Returns HTTP 206 Partial Content
        │     Headers:
        │       Content-Type: audio/mpeg
        │       Content-Range: bytes 0-1048575/3145728
        │       Accept-Ranges: bytes
        │     Payload: Chunked byte stream
        │
Browser Audio Engine (Immediate playback begins without full download)
```

### Download Endpoint Contract:
When the user clicks **Download Audio**, the browser triggers `GET /api/v1/tts/download/{filename}`, which sets:
```http
Content-Disposition: attachment; filename="bloop-speech-42.mp3"
Content-Type: audio/mpeg
```
This forces the browser to save the MP3 directly to the user's local filesystem.

---

## 6. Dynamic Voice Architecture & Ingestion Modes

In strict compliance with the **Dynamic Voice Architecture (Zero Fabricated Voices Rule)**, voice data flows dynamically through four non-hardcoded pathways:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DYNAMIC VOICE INGESTION MODES                       │
├───────────────────────┬─────────────────────────────────────────────────────┤
│ Mode 1: UI Modal      │ User pastes an ElevenLabs Voice ID in the frontend. │
│                       │ Transmitted via POST /api/v1/voices.                │
├───────────────────────┼─────────────────────────────────────────────────────┤
│ Mode 2: Config File   │ Operators define voice mappings in                  │
│                       │ backend/voices_config.json. Ingested at boot or via │
│                       │ POST /api/v1/voices/reload.                         │
├───────────────────────┼─────────────────────────────────────────────────────┤
│ Mode 3: REST API      │ External tools or admins inject voices via          │
│                       │ authenticated POST /api/v1/voices endpoints.        │
├───────────────────────┼─────────────────────────────────────────────────────┤
│ Mode 4: Offline Sim   │ If no API key is provided, SimulationTTSProvider    │
│                       │ generates local waveforms, keeping tests green.     │
└───────────────────────┴─────────────────────────────────────────────────────┘
```

---

## 7. Fault Containment & Failure Scenarios

| Failure Point | System Reaction | User Experience |
| :--- | :--- | :--- |
| **ElevenLabs Outage / Timeout** | `ElevenLabsProvider` raises `ProviderTimeoutError` after 30s. Caught by `TTSService`. | Error toast: *"Text-to-speech provider is currently unavailable. Please try again."* (HTTP 503). |
| **Quota Exceeded (HTTP 429)** | Provider captures ElevenLabs quota limit; translates to `PROVIDER_QUOTA_EXCEEDED`. | Error toast: *"Voice synthesis quota exceeded for this account."* (HTTP 429). |
| **Invalid Voice ID** | Database returns no matching voice or provider rejects ID. | Error toast: *"The selected voice is invalid or inactive."* (HTTP 400). |
| **Disk Storage Write Failure** | `AudioManager` raises `StorageError`. Generation transaction rolled back. | Error toast: *"Failed to save synthesized audio file."* (HTTP 500). Database remains clean. |
