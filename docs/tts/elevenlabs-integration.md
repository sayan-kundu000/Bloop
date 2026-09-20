# ElevenLabs Integration Specification

## 1. Executive Summary

Bloop integrates **ElevenLabs** as its primary natural Text-to-Speech (TTS) provider via an isolated backend adapter (`ElevenLabsProvider`). The integration communicates with the ElevenLabs REST API (`https://api.elevenlabs.io/v1`) using asynchronous HTTPX connections, strict request/response normalization, resilient timeout controls, exponential backoff retries, and comprehensive credential protection.

```
React Client (Vercel)
         │
         │ HTTPS REST /api/v1/tts
         ▼
FastAPI API Gateway (Render)
         │
         ├── Authentication & Rate Limiting (10 req/min)
         ├── Text Processing & Level 2 Validation (Length limits)
         ├── Capability Resolution & Level 3 Validation (Language ↔ Voice compatibility)
         │
   SpeechService
         │
         ▼
   TTSProvider (Interface)
         │
   ElevenLabsProvider (Adapter)
         │
   ElevenLabsClient (HTTPX, timeouts, retry backoff)
         │
         │ Authorization: xi-api-key (Backend-Only)
         ▼
   ElevenLabs REST API (/v1/text-to-speech/{voice_id})
         │
         ▼
   Normalized Audio Bytes & Metadata
         │
         ├── Storage: backend/app/storage/audio/{unique_id}.mp3
         ├── Database: speech_generations table (metadata only, no blobs)
         │
         ▼
   React Audio Player & Direct Download (/api/v1/tts/audio & /download)
```

---

## 2. Security Boundaries & Credential Isolation

1. **Zero Frontend Exposure**: `ELEVENLABS_API_KEY` is loaded strictly on the backend via environment variables (`Settings.ELEVENLABS_API_KEY`). It is never injected into Vite bundles, client build artifacts, or browser payloads.
2. **Log & Exception Scrubbing**: All log outputs are processed by `SecretMaskingFilter`. Exception details and error responses never echo provider keys or tokens.
3. **Git Exclusion**: `.env` and `.env.*` files are gitignored. Production credentials must be supplied via Render environment secrets.

---

## 3. Provider Settings & Parameter Allowlist

Client settings are filtered through `ElevenLabsSettingsMapper` to prevent untrusted JSON parameter injection:

| Parameter | Allowed Range / Values | Default | Description |
| :--- | :--- | :--- | :--- |
| `model_id` | `eleven_multilingual_v2`, `eleven_turbo_v2`, `eleven_turbo_v2_5`, `eleven_monolingual_v1` | `eleven_multilingual_v2` | Core neural synthesis model |
| `stability` | `0.0` to `1.0` (clamped) | `0.5` | Voice stability vs variability |
| `similarity_boost` | `0.0` to `1.0` (clamped) | `0.75` | Proximity to original training voice |
| `style` | `0.0` to `1.0` (clamped) | `0.0` | Exaggeration of original delivery style |
| `use_speaker_boost` | `true`, `false` | `true` | Enhances clarity and volume |
| `output_format` | `mp3_44100_128`, `mp3_44100_64`, `mp3_44100_192`, `pcm_16000`, `pcm_22050`, `pcm_44100` | `mp3_44100_128` | Audio container and sample rate |

---

## 4. Resilience & Error Mapping

| ElevenLabs HTTP Status | Internal Domain Exception | Bloop API Error Code | HTTP Status | Retry Behavior |
| :--- | :--- | :--- | :--- | :--- |
| **401 Unauthorized** | `ElevenLabsAuthenticationException` | `TTS_PROVIDER_UNAVAILABLE` | `503` | **Do not retry** |
| **404 Not Found** | `ElevenLabsVoiceNotFoundException` | `INVALID_VOICE` | `422` | **Do not retry** |
| **429 Rate Limited** | `ElevenLabsRateLimitException` | `RATE_LIMIT_EXCEEDED` | `429` | **Do not retry** |
| **400 / 422 Bad Payload**| `ElevenLabsValidationException` | `VALIDATION_ERROR` | `422` | **Do not retry** |
| **500 / 502 / 503 / 504**| `ElevenLabsUnavailableException` | `TTS_PROVIDER_UNAVAILABLE` | `503` | **Retry (max 2) with backoff** |
| **Timeout (Connect/Read)**| `ElevenLabsTimeoutException` | `TTS_PROVIDER_UNAVAILABLE` | `504` | **Retry (max 2) with backoff** |
