# ADR-005: ElevenLabs Provider Abstraction and Offline Simulation Fallback

## Status
**Accepted**

## Context
Bloop delivers commercial-grade AI voice synthesis through integration with the ElevenLabs REST API. However, directly coupling application routes or services to ElevenLabs SDK specifics introduces significant failure modes:
1. Hardcoded vendor locks that prevent future integration of alternative providers (e.g. Azure Speech, Amazon Polly, local TTS models).
2. Failure of automated test suites and local development whenever `ELEVENLABS_API_KEY` is absent, expired, or depleted.
3. Accidental leakage of third-party API keys to client-side bundles.

## Decision
1. Establish a formal `BaseTTSProvider` abstract base class defining `synthesize()`, `is_configured()`, and `provider_name`.
2. Implement `ElevenLabsProvider` encapsulating all HTTP communication with `https://api.elevenlabs.io/v1/text-to-speech/{voice_id}` using `httpx.AsyncClient`.
3. Implement `SimulationTTSProvider` that synthesizes local sinusoidal audio waveforms whenever `ELEVENLABS_API_KEY` is not configured or in testing environments.
4. Keep all ElevenLabs credentials strictly server-side in `.env` and Render secrets; the React client never communicates directly with ElevenLabs or sees the API key.
5. Adhere strictly to the **Zero Fabricated Voices Rule**: do not populate the voice registry with fake voice IDs or arbitrary mock catalogues. Voice records are ingested dynamically at runtime.

## Alternatives Considered
1. **Direct ElevenLabs SDK Binding in Routes:** Calling ElevenLabs directly from FastAPI endpoints. Rejected because it violates Clean Architecture, tightly couples routes to vendor code, and breaks offline testing.
2. **Client-Side ElevenLabs SDK:** Making ElevenLabs requests directly from the React frontend. Rejected because it would expose `ELEVENLABS_API_KEY` to public browser network inspections, leading to catastrophic credential theft.

## Consequences

### Positive
- **Complete Vendor Decoupling:** The core `TTSService` depends exclusively on `BaseTTSProvider`. Future providers can be added without altering business logic or API routes.
- **100% Offline Testability:** Local developers and automated CI runners execute full end-to-end tests without requiring paid ElevenLabs API credits or active network connections.
- **Safe Error Normalization:** ElevenLabs rate limits (HTTP 429), timeouts, and auth failures (HTTP 401) are trapped and translated into normalized JSON envelopes without exposing internal vendor errors.

### Negative / Trade-offs
- **Simulation Audio Fidelity:** Offline simulation generates synthetic tones rather than natural human speech; sufficient for testing audio pipeline integrity, but cannot validate speech pronunciation.
