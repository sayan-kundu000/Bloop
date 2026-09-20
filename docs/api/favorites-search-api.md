# Favorites & History Search REST API Contracts

All endpoints are authenticated and operate within the `/api/v1` namespace.

---

## 1. List Favorites

### `GET /api/v1/favorites`
Retrieve a paginated list of the authenticated user's bookmarked speech generations.

#### Query Parameters:
- `search` (optional string): Substring search matching generation text, voice name, or bookmark label.
- `language` (optional string): BCP-47 language code filter (e.g. `en-US`).
- `page` (optional integer, default `1`, min `1`): 1-indexed page number.
- `page_size` (optional integer, default `20`, min `1`, max `100`): Records per page.

#### Response (200 OK):
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 14,
        "user_id": 1,
        "generation_id": 42,
        "label": "Demo Intro",
        "created_at": "2026-09-17T20:15:30Z",
        "generation": {
          "id": 42,
          "user_id": 1,
          "text": "Welcome to Bloop Quantum Speech synthesis.",
          "char_count": 42,
          "word_count": 6,
          "language_code": "en-US",
          "voice_id": "v-quantum-1",
          "voice_name": "Aether",
          "status": "completed",
          "audio_url": "/api/v1/tts/audio/speech-42.mp3",
          "download_url": "/api/v1/tts/download/speech-42.mp3",
          "duration_seconds": 2.8,
          "file_size_bytes": 45000,
          "provider": "elevenlabs",
          "is_favorite": true,
          "favorite_id": 14,
          "created_at": "2026-09-17T20:10:00Z"
        }
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20,
    "has_next": false,
    "has_prev": false,
    "total_pages": 1
  },
  "meta": {
    "page": 1,
    "page_size": 20,
    "total": 1,
    "total_pages": 1,
    "has_next": false,
    "has_prev": false
  },
  "message": "Favorites retrieved successfully."
}
```

---

## 2. Add Favorite

### `POST /api/v1/favorites`
Bookmark an existing speech generation.

#### Request Body:
```json
{
  "generation_id": 42,
  "label": "Important Audio Note"
}
```

#### Response (201 Created):
```json
{
  "success": true,
  "data": {
    "id": 15,
    "user_id": 1,
    "generation_id": 42,
    "label": "Important Audio Note",
    "created_at": "2026-09-17T21:00:00Z",
    "generation": {
      "id": 42,
      "text": "Welcome to Bloop Quantum Speech synthesis.",
      "is_favorite": true,
      "favorite_id": 15
    }
  },
  "message": "Added to favorites successfully."
}
```

#### Errors:
- `404 Not Found`: Target generation ID does not exist (`GENERATION_NOT_FOUND`).
- `403 Forbidden`: Target generation belongs to another user (`FORBIDDEN`).
- `409 Conflict`: Target generation is already bookmarked (`CONFLICT`).

---

## 3. Remove Favorite

### `DELETE /api/v1/favorites/{favorite_id}`
Delete a favorite bookmark by favorite ID.

#### Response (200 OK):
```json
{
  "success": true,
  "data": {
    "deleted_id": 15,
    "message": "Favorite removed."
  },
  "message": "Removed from favorites successfully."
}
```

### `DELETE /api/v1/favorites/generation/{generation_id}`
Delete a favorite bookmark by generation ID (convenience toggle).

---

## 4. Search & Filter History

### `GET /api/v1/history`
Query user speech generations with search, multi-factor filtering, and sorting.

#### Query Parameters:
- `search` (optional string, max 100): Case-insensitive keyword matching text and voice name.
- `language` (optional string): Exact BCP-47 language code filter.
- `status` (optional string): Lifecycle state (`completed`, `failed`, `pending`, `processing`).
- `favorite` (optional boolean): Filter only bookmarked items (`true`) or non-bookmarked (`false`).
- `created_after` (optional ISO 8601 string): Lower bound timestamp.
- `created_before` (optional ISO 8601 string): Upper bound timestamp.
- `sort_by` (optional string, default `created_at`): Allowlist: `created_at`, `duration_seconds`, `char_count`, `word_count`.
- `order` (optional string, default `desc`): `asc` or `desc`.
- `page` (optional integer, default `1`, min `1`).
- `page_size` (optional integer, default `20`, min `1`, max `100`).
