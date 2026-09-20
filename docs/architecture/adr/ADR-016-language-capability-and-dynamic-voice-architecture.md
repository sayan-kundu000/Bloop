# ADR-016: Language Capability Mapping & Dynamic Voice Architecture

## Status
Accepted

## Context
In text-to-speech platforms, tightly coupling language metadata, external vendor voice identifiers, and application voice selection creates fragile architectures that break when switching providers or introducing multilingual voices.

Specifically:
1. Vendor Voice ID Leakage: Directly using third-party vendor voice identifiers (e.g., ElevenLabs IDs) in frontend components, URLs, or client-facing database records leaks proprietary vendor internals and prevents seamless provider migration.
2. 1:1 Voice-Language Assumptions: A single voice in modern neural TTS can support multiple languages/locales (polyglot voices), requiring a flexible many-to-many capability architecture.
3. Provider Cost & Quota Waste: Allowing requests with invalid languages, invalid voices, or mismatched language-voice pairs to reach external synthesis APIs wastes paid character quotas, exhausts rate limits, and increases network latency.
4. Hardcoded Voice Catalogs: Embedding voice names, IDs, or static catalogs in frontend bundles or application source code requires full code redeployments to add, rename, or retire voices.

## Decision
We implement a decoupled, dynamic, three-tier capability architecture:

1. **Four-Way Separation of Concerns:**
   - **Language Metadata:** Canonical BCP-47 / ISO tags, localized native names, text direction (`ltr`/`rtl`), and locale metadata (`languages` table).
   - **Provider Capability:** External vendor support tracking vs. Bloop application enablement (`provider_capabilities` table).
   - **Voice Capability:** Public application identifier (`voice_id`), isolated internal vendor ID (`provider_voice_id`), and traits (`voices` table).
   - **Voice-Language Compatibility:** Dynamic many-to-many relationship mapping voices to their supported languages (`voice_language_capabilities` table).

2. **Provider Voice ID Abstraction:**
   - The public API exposes only application `voice_id` handles (e.g. `voice-serena-natural`).
   - The raw vendor ID (e.g., ElevenLabs ID) is stored exclusively in `provider_voice_id` and is strictly never serialized in API responses or logs.

3. **Authoritative Backend Level 3 Validation:**
   - Before invoking synthesis providers, `CapabilityService.validate_tts_capability()` checks language availability, voice availability, and voice-language compatibility.
   - Failures raise dedicated validation exceptions (`INVALID_LANGUAGE`, `INVALID_VOICE`, `VOICE_LANGUAGE_MISMATCH`) returning HTTP `422 Unprocessable Entity`.
   - **Guaranteed Provider Non-Invocation:** Synthesis providers are strictly never called on capability validation failure.

4. **Zero Hardcoded Production Voices:**
   - The production catalog begins 100% empty.
   - Voices are registered dynamically through configuration files (`voices_config.json`), administrative dynamic registration (`POST /api/v1/voices`), or database migration.

## Consequences
### Positive
- **Vendor Agnostic:** Bloop can switch or add speech providers (e.g. AWS Polly, Azure Speech, self-hosted models) without changing public voice IDs, schemas, or frontend UI bindings.
- **Provider Protection:** Eliminates quota burn and rate limit consumption from invalid voice or language synthesis attempts.
- **Polyglot Ready:** Voices seamlessly support multiple languages through M2M capability links while maintaining backward compatibility with single-language voices.
- **Dynamic Extensibility:** Adding voices or languages requires zero code changes or client redeployments.

### Negative
- Requires a database query to resolve voice-language capability mappings prior to synthesis (mitigated by database indexes on `voices.voice_id`, `languages.code`, and capability foreign keys).
