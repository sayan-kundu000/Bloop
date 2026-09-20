# Bloop REST API — Speech Synthesis (TTS) Specification

## 1. Overview

The **Speech (TTS) Domain** coordinates neural voice synthesis, audio caching, quantum parameter modulation, real-time HTTP Range streaming, and pre-synthesis text metrics analysis.

---

## 2. Endpoints

### 2.1 Synthesize Speech

Initiates text-to-speech synthesis with optional quantum modulation and acoustic controls.

- **Method:** `POST`
- **Path:** `/api/v1/tts`
- **Access:** Public or Authenticated (Authenticating associates record with user history)
- **Success Status:** `200 OK`

#### Request Payload (`TTSRequest`)
```json
{
  "text": "Welcome to Bloop. Seamless speech synthesis powered by quantum intelligence.",
  "voice_id": "sim_voice_narrator",
  "language": "en-US",
  "speed": 1.0,
  "pitch": 0.0,
  "emotion": "neutral",
  "quantum_modulation": true
}
```

| Field | Type | Required | Range / Pattern | Description |
| :--- | :--- | :--- | :--- | :--- |
| `text` | `string` | Yes | `1 <= chars <= 2500` | Input text to synthesize (enforces `MAX_TEXT_CHARACTERS`) |
| `voice_id` | `string` | Yes | Max 50 chars | Target voice identifier from `/api/v1/voices` |
| `language` | `string` | No | BCP-47 (default: `en-US`) | Target linguistic locale |
| `speed` | `float` | No | `0.5 <= x <= 2.0` | Playback speed rate multiplier |
| `pitch` | `float` | No | `-20.0 <= x <= 20.0` | Fundamental frequency pitch shift in semitones |
| `emotion` | `string` | No | Enum / String | Target emotional coloring |
| `quantum_modulation` | `boolean` | No | Default: `true` | Apply QNN sentiment modulation |

#### Success Response (`ApiResponse[TTSResponse]`)
```json
{
  "success": true,
  "data": {
    "generation_id": 142,
    "status": "completed",
    "audio_url": "/api/v1/tts/stream/142",
    "download_url": "/api/v1/tts/download/142",
    "duration_seconds": 4.82,
    "char_count": 76,
    "word_count": 10,
    "voice_id": "sim_voice_narrator",
    "voice_name": "Neural Narrator",
    "language_code": "en-US",
    "provider": "simulation",
    "file_size_bytes": 154240,
    "created_at": "2026-09-17T18:10:00Z"
  },
  "message": "Speech generated successfully."
}
```

#### Error Responses
- **422 Unprocessable Entity (`TEXT_EMPTY`):** Input text is empty, None, or solely whitespace.
  ```json
  {
    "success": false,
    "error": {
      "code": "TEXT_EMPTY",
      "message": "Text cannot be empty",
      "details": { "reason": "empty_or_whitespace_only" }
    }
  }
  ```
- **422 Unprocessable Entity (`TEXT_TOO_LONG`):** Input text exceeds `MAX_TEXT_CHARACTERS` (2,500 characters).
  ```json
  {
    "success": false,
    "error": {
      "code": "TEXT_TOO_LONG",
      "message": "Text exceeds the maximum allowed length",
      "details": { "max_characters": 2500, "actual_characters": 2501 }
    }
  }
  ```
- **422 Unprocessable Entity (`INVALID_LANGUAGE`):** Requested language is not configured or inactive.
  ```json
  {
    "success": false,
    "error": {
      "code": "INVALID_LANGUAGE",
      "message": "The selected language is not available",
      "details": { "language_code": "xx-YY" }
    }
  }
  ```
- **422 Unprocessable Entity (`INVALID_VOICE`):** Requested voice is not found or inactive.
  ```json
  {
    "success": false,
    "error": {
      "code": "INVALID_VOICE",
      "message": "The selected voice is not available",
      "details": { "voice_id": "unknown_voice" }
    }
  }
  ```
- **422 Unprocessable Entity (`VOICE_LANGUAGE_MISMATCH`):** Voice does not support the requested language locale.
  ```json
  {
    "success": false,
    "error": {
      "code": "VOICE_LANGUAGE_MISMATCH",
      "message": "Voice 'normal-female' does not support language 'fr-FR'",
      "details": { "voice_id": "normal-female", "language_code": "fr-FR" }
    }
  }
  ```
- **422 Unprocessable Entity (`VALIDATION_ERROR`):** Malformed request payload.
- **502 Bad Gateway (`TTS_PROVIDER_UNAVAILABLE` / `PROVIDER_ERROR`):** Synthesis backend failed or timed out.


---

### 2.2 Stream Audio with HTTP Range Support

Streams synthesized audio binaries, fully supporting `Range: bytes=start-end` requests for seamless scrubbing and mobile audio players.

- **Method:** `GET`
- **Path:** `/api/v1/tts/stream/{generation_id}`
- **Headers Handled:** `Range: bytes=0-`
- **Response Headers:** `Content-Type: audio/mpeg` (or `audio/wav`), `Accept-Ranges: bytes`, `Content-Length`, `Content-Range`
- **Success Status:** `200 OK` (Full audio) or `206 Partial Content` (Range chunk)

---

### 2.3 Download Audio File

Directly downloads the synthesized audio file with forced attachment disposition.

- **Method:** `GET`
- **Path:** `/api/v1/tts/download/{generation_id}`
- **Response Headers:** `Content-Disposition: attachment; filename="bloop_generation_142.mp3"`
- **Success Status:** `200 OK`

---

### 2.4 Pre-Synthesis Text Metrics Analysis

Computes character, word, sentence, duration estimations, and readability indices before initiating synthesis.

- **Method:** `POST`
- **Path:** `/api/v1/tts/analyze`
- **Access:** Public (No authentication required)
- **Success Status:** `200 OK`

#### Request Payload (`TextAnalyzeRequest`)
```json
{
  "text": "The quantum superposition principle allows simultaneous multi-state exploration.",
  "speaking_rate_wpm": 150
}
```

#### Success Response (`ApiResponse[TextAnalyzeResponse]`)
```json
{
  "success": true,
  "data": {
    "char_count": 83,
    "word_count": 9,
    "sentence_count": 1,
    "estimated_duration_seconds": 3.6,
    "speaking_rate_wpm": 150,
    "readability_score": 45.2,
    "detected_sentiment": "analytical"
  },
  "message": "Text analyzed successfully."
}
```
