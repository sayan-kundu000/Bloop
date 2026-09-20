# Architecture: TTS Provider Boundary & Security Isolation

## 1. Security Architecture

```
                                 PUBLIC CLIENT (BROWSER)
                                            │
                                            │ HTTPS REST
                                            ▼
                             FASTAPI API GATEWAY (RENDER)
                                            │
               ┌────────────────────────────┼────────────────────────────┐
               │                            │                            │
               ▼                            ▼                            ▼
      POSTGRESQL DATABASE             LOCAL DISK STORAGE            ELEVENLABS API
       (Metadata Only)               (Temporary Audio)              (Backend-Only)
   • speech_generations          • unique_id.mp3                • xi-api-key header
   • NO audio blobs              • range streaming              • NO client exposure
```

---

## 2. Dynamic Voice Isolation

In accordance with Bloop's dynamic voice architecture:
- **No Production Voice Catalog Hardcoding**: The application does not pre-populate hardcoded ElevenLabs voice IDs in production.
- **Provider Voice ID Masking**: The database model `Voice` maintains `provider_voice_id` internally, exposing only the abstract Bloop `voice_id` to public APIs.
- **No Live Discovery on Startup**: The server never executes voice-listing network calls on startup or on every synthesis request.
