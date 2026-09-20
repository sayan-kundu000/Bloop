# Profile, Preferences & History REST API Specification

This document specifies the REST contracts, query parameters, authorization headers, and error response envelopes for the user profile, preference, and speech generation history endpoints in Bloop.

---

## 1. User Profile API

### `GET /api/v1/users/me`
* **Description**: Retrieves the authenticated user's profile and embedded preferences.
* **Authentication**: Required (HttpOnly `access_token` cookie or `Authorization: Bearer <token>`).
* **Response `200 OK`**:
  ```json
  {
    "success": true,
    "data": {
      "id": 1,
      "email": "user@bloop.ai",
      "full_name": "Dr. Quantum",
      "is_active": true,
      "is_superuser": false,
      "created_at": "2026-09-17T20:00:00Z",
      "preference": {
        "id": 1,
        "user_id": 1,
        "theme": "dark",
        "audio_speed": 1.0,
        "auto_play": true,
        "default_language_code": "en-US",
        "default_voice_id": null
      }
    },
    "message": "User profile retrieved successfully."
  }
  ```

### `PATCH /api/v1/users/me`
* **Description**: Updates permitted user profile attributes (`full_name`).
* **Authentication**: Required.
* **Request Body**:
  ```json
  {
    "full_name": "Dr. Quantum Updated"
  }
  ```
* **Security Invariant**: Any attempt to pass `password`, `email`, or role flags is ignored and safely rejected from mutation.

---

## 2. User Preferences API

### `GET /api/v1/users/me/preferences`
* **Description**: Retrieves user application settings and synthesis defaults.
* **Authentication**: Required.
* **Response `200 OK`**:
  ```json
  {
    "success": true,
    "data": {
      "id": 1,
      "user_id": 1,
      "theme": "dark",
      "audio_speed": 1.25,
      "auto_play": true,
      "default_language_code": "en-US",
      "default_voice_id": null
    },
    "message": "Preferences retrieved successfully."
  }
  ```

### `PATCH /api/v1/users/me/preferences`
* **Description**: Updates UI theme, playback speed multiplier, auto-play flag, or default language/voice.
* **Authentication**: Required.
* **Request Body**:
  ```json
  {
    "theme": "light",
    "audio_speed": 1.2,
    "auto_play": false,
    "default_language_code": "en-US",
    "default_voice_id": null
  }
  ```
* **Validation Rules**:
  - `theme`: Must be `'dark'`, `'light'`, or `'system'`.
  - `audio_speed`: Float between `0.5` and `2.0`.
  - `default_language_code`: Must match an active registered language code, or `null` to clear.
  - `default_voice_id`: String up to 100 characters or `null`.

---

## 3. Speech History API

### `GET /api/v1/history`
* **Description**: Retrieves paginated speech generation records scoped strictly to the requesting user.
* **Authentication**: Required.
* **Query Parameters**:
  - `search` (string, optional): Search keyword across synthesized text and voice display name.
  - `language` (string, optional): Exact BCP-47 language locale (e.g. `en-US`).
  - `status` (string, optional): Lifecycle status filter (`completed`, `failed`).
  - `sort_by` (string, optional): Allowlisted attribute (`created_at`, `duration_seconds`, `char_count`, `word_count`). Default: `created_at`.
  - `order` (string, optional): `desc` (default) or `asc`.
  - `page` (integer, optional): 1-indexed page number (default: 1).
  - `page_size` (integer, optional): Items per page (default: 20, max: 100).
* **Response `200 OK`**:
  ```json
  {
    "success": true,
    "data": {
      "items": [
        {
          "id": 42,
          "user_id": 1,
          "text": "Simulated quantum speech synthesis output.",
          "char_count": 43,
          "word_count": 5,
          "language_code": "en-US",
          "voice_id": "v-quantum-1",
          "voice_name": "Quantum Synthesizer",
          "status": "completed",
          "audio_url": "/api/v1/tts/audio/9a8b7c6d.mp3",
          "download_url": "/api/v1/tts/download/9a8b7c6d.mp3",
          "duration_seconds": 3.2,
          "file_size_bytes": 51200,
          "provider": "elevenlabs",
          "is_favorite": false,
          "favorite_id": null,
          "created_at": "2026-09-17T20:30:00Z"
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
    "message": "History retrieved successfully."
  }
  ```

### `GET /api/v1/history/{generation_id}`
* **Description**: Retrieves detailed metadata and audio URLs for a single generation record.
* **Authentication**: Required.
* **Authorization**: Must be owned by requesting user (`gen.user_id == current_user.id`) or superuser.
* **Response `403 Forbidden`**: Returned if record belongs to another user.
* **Response `404 Not Found`**: Returned if record does not exist.

### `DELETE /api/v1/history/{generation_id}`
* **Description**: Deletes a speech generation record and cleans up its temporary audio asset from disk.
* **Authentication**: Required.
* **Authorization**: Must be owned by requesting user.
* **Response `200 OK`**:
  ```json
  {
    "success": true,
    "data": {
      "deleted_id": 42
    },
    "message": "Generation deleted successfully."
  }
  ```
