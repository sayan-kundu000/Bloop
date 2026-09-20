# ADR-004: ElevenLabs Provider Isolation and Offline Simulation Fallback

## Status
**Accepted**

## Context
Bloop provides speech synthesis by connecting to ElevenLabs' commercial REST API. However, directly coupling the FastAPI web routes or business logic to ElevenLabs SDK details introduces several severe failure vectors:
1. Leaking third-party vendor interfaces throughout the application.
2. Vendor lock-in preventing future integration of alternate TTS engines (e.g., Azure Speech, Amazon Polly, or local open-source models).
3. Breaking local development and automated CI testing whenever an ElevenLabs API key is missing, exhausted, or rate-limited.
4. Exposing ElevenLabs API credentials to client-side bundles.

## Decision
1. **Abstract Provider Interface:** Define `BaseTTSProvider` as an abstract base class (`abc.ABC`) specifying `synthesize()`, `is_configured()`, and `provider_name`.
2. **Dedicated ElevenLabs Implementation:** Implement `ElevenLabsProvider` encapsulating all HTTP communication with `https://api.elevenlabs.io/v1/text-to-speech/{voice_id}` using `httpx.AsyncClient`.
3. **Automatic Simulation Fallback:** Implement `SimulationTTSProvider` which generates synthetic audio tones locally when `ELEVENLABS_API_KEY` is not configured or in testing environments.
4. **Complete Credential Isolation:** All API keys reside strictly on the server in `.env`. Client requests pass only abstract voice IDs and text payloads.

## Rationale
1. **Dependency Inversion Principle:** The high-level `TTSService` depends on the abstraction `BaseTTSProvider`, not on the concrete `ElevenLabsProvider`.
2. **Zero Cost & Offline Testing:** Developers can clone, run, and run automated test suites without paying for ElevenLabs credits or failing on CI pipelines.
3. **Failure Containment:** ElevenLabs network timeouts, HTTP 401 unauthorized errors, and HTTP 429 quota exceedances are trapped inside `ElevenLabsProvider` and translated into normalized domain errors (`ProviderError`, `ProviderQuotaExceededError`) with safe JSON error envelopes.

## Consequences
### Positive
- Future TTS engines can be integrated by implementing `BaseTTSProvider` without changing routers or services.
- Test suites run 100% reliably in offline CI runners.
- API keys are never exposed in browser network requests or bundle artifacts.

### Negative / Trade-offs
- Simulation provider audio generates synthetic tonal waveforms rather than natural speech, suitable for testing pipeline integrity but not for speech quality evaluation.
