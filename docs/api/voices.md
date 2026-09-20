# Bloop REST API — Voices Domain Specification

## 1. Overview & Dynamic Architecture

The **Voices Domain** provides dynamic discovery, search, and capability filtering across available synthetic and neural voices without hardcoded assumptions.

### Dynamic Voice Registry Architectural Guarantees
1. **Zero Hardcoded Voice Data:** Bloop does not embed static voice catalogs, third-party vendor names, or proprietary voice identifiers into source code or schemas.
2. **Provider Voice ID Abstraction:** Internal vendor voice identifiers (e.g. raw ElevenLabs IDs) are stored in `provider_voice_id` and **never exposed** in client responses. Clients interact solely with application `voice_id` handles.
3. **Multi-Locale Compatibility:** Voices support one or more BCP-47 language tags through direct primary locale keys and many-to-many (`VoiceLanguageCapability`) mappings.
4. **Empty Catalog Resilience:** An unconfigured catalog returns `{"success": true, "data": []}` cleanly without throwing errors or halting the frontend.

---

## 2. Endpoints

### 2.1 List and Filter Voices

Queries dynamically available voices with multi-dimensional filtering.

- **Method:** `GET`
- **Path:** `/api/v1/voices`
- **Access:** Public (No authentication required)
- **Success Status:** `200 OK`

#### Query Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `language` | `string` | No | Filter by language locale code (e.g. `en-US`, `es-ES`) |
| `language_code`| `string` | No | Alias for `language` filter |
| `gender` | `string` | No | Filter by voice gender (`male`, `female`, `neutral`, `all`) |
| `search` | `string` | No | Substring search across voice name, accent, description, or ID |

#### Response (`ApiResponse[List[VoiceResponse]]`)
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "voice_id": "normal-female",
      "name": "Normal Female",
      "language_code": "en-US",
      "supported_languages": ["en-US", "es-ES"],
      "gender": "female",
      "accent": "American",
      "description": "Standard natural American English female voice.",
      "provider": "dynamic",
      "preview_url": null,
      "is_active": true,
      "is_user_configured": false,
      "metadata": null
    }
  ],
  "message": "Voices retrieved successfully"
}
```

#### Empty Catalog Response
```json
{
  "success": true,
  "data": [],
  "message": "Voices retrieved successfully"
}
```

---

### 2.2 Get Single Voice by ID

Retrieves details for a specific voice by its application-level `voice_id`.

- **Method:** `GET`
- **Path:** `/api/v1/voices/{voice_id}`
- **Access:** Public
- **Success Status:** `200 OK`

#### Error Response (404 Not Found)
```json
{
  "success": false,
  "error": {
    "code": "VOICE_NOT_FOUND",
    "message": "Voice 'unknown_voice' not found or inactive",
    "details": {}
  }
}
```

---

### 2.3 Dynamically Register Voice

Enables dynamic registration of custom or user-provided voices (e.g. an ElevenLabs voice ID) without backend code changes.

- **Method:** `POST`
- **Path:** `/api/v1/voices`
- **Access:** Public / Authenticated
- **Success Status:** `200 OK`

#### Request Payload (`VoiceCreate`)
```json
{
  "voice_id": "custom-narrator-01",
  "provider_voice_id": "21m00Tcm4TlvDq8ikWAM",
  "name": "Custom Studio Narrator",
  "language_code": "en-US",
  "gender": "neutral",
  "accent": "Mid-Atlantic",
  "description": "High-fidelity audio narration voice.",
  "provider": "elevenlabs"
}
```

---

## 3. Schema Definitions

### `VoiceResponse`
| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `integer` | Database surrogate primary key |
| `voice_id` | `string` | Public application voice identifier |
| `name` | `string` | Human-readable voice name |
| `language_code` | `string` | Primary language locale code |
| `supported_languages`| `array[string]` | All language codes supported by this voice |
| `gender` | `string` | Voice gender category (`female`, `male`, `neutral`, `unspecified`) |
| `accent` | `string` (nullable) | Regional accent or dialect descriptor |
| `description` | `string` (nullable) | Acoustic qualities and characteristics summary |
| `provider` | `string` | Synthesis provider (`elevenlabs`, `dynamic`, `simulation`) |
| `preview_url` | `string` (nullable) | Audio sample audition URL |
| `is_active` | `boolean` | Availability status for synthesis |
| `is_user_configured` | `boolean` | Flag indicating user/dynamic registration |
| `metadata` | `object` (nullable) | Extensible style and acoustic flags |
