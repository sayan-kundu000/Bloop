# TTS Troubleshooting Guide

## 1. Common Provider Errors & Resolutions

### `TTS_PROVIDER_UNAVAILABLE` (HTTP 503)
- **Cause**: ElevenLabs API key is missing or invalid, or remote ElevenLabs service is experiencing outages.
- **Resolution**:
  1. Check backend `.env` has `ELEVENLABS_API_KEY` populated with a valid key.
  2. For production on Render, verify that the environment secret `ELEVENLABS_API_KEY` is added to the service dashboard.
  3. Verify network connectivity to `https://api.elevenlabs.io/v1`.

---

### `RATE_LIMIT_EXCEEDED` (HTTP 429)
- **Cause**: Either application-level rate limiting (10 requests/minute per IP) was exceeded, or the ElevenLabs account quota ran out.
- **Resolution**:
  1. If application-level: wait for the `retry_after_seconds` returned in the error response payload.
  2. If provider-level: check ElevenLabs subscription character usage in your ElevenLabs dashboard.

---

### `INVALID_VOICE` (HTTP 422)
- **Cause**: The requested `voice_id` does not exist in Bloop's dynamic voice catalog or is disabled.
- **Resolution**:
  1. Query `GET /api/v1/voices` to view currently registered and active voices.
  2. Ensure the voice is configured with `is_active=true`.

---

### `VOICE_LANGUAGE_MISMATCH` (HTTP 422)
- **Cause**: The requested voice does not support the selected language locale.
- **Resolution**:
  1. Query `GET /api/v1/voices?language={code}` to find voices compatible with the chosen language.
