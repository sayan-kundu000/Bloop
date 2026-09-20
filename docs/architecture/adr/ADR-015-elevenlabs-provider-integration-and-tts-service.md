# ADR-015: ElevenLabs Provider Integration & Secure Speech Service Engine

## Status
**ACCEPTED**

## Date
2026-09-17

## Context
Bloop requires real, natural-sounding Text-to-Speech synthesis backed by ElevenLabs. However, exposing vendor-specific SDK details, embedding API keys in frontend code, or coupling domain models to ElevenLabs response formats would violate Bloop's security posture and architectural neutrality.

Furthermore, dynamic voice resolution requires that no actual production voices or fake voice catalogs be hardcoded in the codebase, preserving flexibility for user configuration.

## Decision
1. **Provider Abstraction**:
   - Established abstract interface `TTSProvider` and normalized `TTSProviderResult`.
   - Built a modular package `backend/app/providers/elevenlabs/` containing:
     - `client.py`: HTTPX client with explicit timeouts (5s connect, 30s read), exponential backoff on 5xx errors, and header correlation.
     - `mapper.py`: Allowlist filter for synthesis parameters, clamping voice settings and mapping ISO language codes.
     - `exceptions.py`: Translation of HTTP status codes into domain exceptions.
     - `provider.py`: Adapter producing `TTSProviderResult`.
2. **Speech Orchestration Service**:
   - Implemented `SpeechService` in `backend/app/services/speech/` to orchestrate text validation (Level 2), capability resolution (Level 3), optional quantum modulation, provider execution, and transactional metadata persistence.
   - Retained `TTSService` as a backward-compatible wrapper for existing endpoints and tests.
3. **Security Boundaries**:
   - `ELEVENLABS_API_KEY` is exclusively read by the backend environment and masked across all logs via `SecretMaskingFilter`.
   - Never exposed to React or browser clients.
4. **Temporary Audio Delivery**:
   - Generation metadata is recorded in PostgreSQL. Audio binary data is saved to temporary local storage (`backend/app/storage/audio/`) and served with HTTP Range streaming (`/api/v1/tts/audio/{filename}`).

## Consequences
- **Positive**: Clean provider separation, zero credential leakage, robust resilience with retries and timeouts, complete test isolation via mocks.
- **Trade-off**: Requires backend proxying of audio requests rather than direct client-to-vendor streaming, which is intentional to preserve key security.
