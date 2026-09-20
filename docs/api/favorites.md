# Bloop REST API — Favorites Domain Specification

## 1. Overview

The **Favorites Domain** allows authenticated users to bookmark exceptional speech generations into their curated library with custom labels. The system enforces strict relational constraints:
- **Uniqueness Constraint:** A user cannot favorite the same speech generation record more than once. Attempting to do so triggers an explicit `409 Conflict` (`RESOURCE_CONFLICT` / `CONFLICT`).
- **Ownership Verification:** A favorite record can only be viewed or removed by its owner. Attempting to delete another user's bookmark yields `403 Forbidden` (`ACCESS_DENIED` / `FORBIDDEN`).

---

## 2. Endpoints

### 2.1 List Bookmarked Favorites

Retrieves a paginated list of favorited generations for the current user, embedding full generation details.

- **Method:** `GET`
- **Path:** `/api/v1/favorites`
- **Access:** Authenticated (`Authorization: Bearer <token>`)
- **Success Status:** `200 OK`

#### Query Parameters

| Parameter | Type | Default | Constraints | Description |
| :--- | :--- | :--- | :--- | :--- |
| `page` | `integer` | `1` | `>= 1` | 1-indexed page number |
| `page_size`| `integer` | `20`| `1 <= x <= 100` | Items per page |

#### Response (`ApiResponse[PaginatedResponse[FavoriteResponse]]`)
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 12,
        "user_id": 1,
        "generation_id": 142,
        "label": "Marketing Voiceover Key Take",
        "created_at": "2026-09-17T18:12:00Z",
        "generation": {
          "id": 142,
          "user_id": 1,
          "text": "Speech synthesis prompt text.",
          "char_count": 29,
          "word_count": 4,
          "language_code": "en-US",
          "voice_id": "sim_voice_narrator",
          "voice_name": "Neural Narrator",
          "status": "completed",
          "audio_url": "/api/v1/tts/stream/142",
          "download_url": "/api/v1/tts/download/142",
          "duration_seconds": 2.1,
          "file_size_bytes": 67328,
          "provider": "simulation",
          "is_favorite": true,
          "favorite_id": 12,
          "created_at": "2026-09-17T18:10:00Z"
        }
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20,
    "total_pages": 1,
    "has_next": false,
    "has_prev": false
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

### 2.2 Add Favorite Bookmark

Bookmarks a speech generation record.

- **Method:** `POST`
- **Path:** `/api/v1/favorites`
- **Access:** Authenticated (`Authorization: Bearer <token>`)
- **Success Status:** `201 Created`

#### Request Payload (`FavoriteCreate`)
```json
{
  "generation_id": 142,
  "label": "Marketing Voiceover Key Take"
}
```

#### Success Response (`201 Created`)
```json
{
  "success": true,
  "data": {
    "id": 12,
    "user_id": 1,
    "generation_id": 142,
    "label": "Marketing Voiceover Key Take",
    "created_at": "2026-09-17T18:12:00Z",
    "generation": {
      "id": 142,
      "user_id": 1,
      "text": "Speech synthesis prompt text.",
      "char_count": 29,
      "word_count": 4,
      "language_code": "en-US",
      "voice_id": "sim_voice_narrator",
      "voice_name": "Neural Narrator",
      "status": "completed",
      "audio_url": "/api/v1/tts/stream/142",
      "download_url": "/api/v1/tts/download/142",
      "duration_seconds": 2.1,
      "file_size_bytes": 67328,
      "provider": "simulation",
      "is_favorite": true,
      "favorite_id": 12,
      "created_at": "2026-09-17T18:10:00Z"
    }
  },
  "message": "Added to favorites successfully."
}
```

#### Error Responses
- **404 Not Found (`RESOURCE_NOT_FOUND`):** Generation record `142` does not exist.
- **409 Conflict (`RESOURCE_CONFLICT` / `CONFLICT`):** Generation is already bookmarked by the user.

---

### 2.3 Remove Favorite Bookmark

Deletes an existing bookmark.

- **Method:** `DELETE`
- **Path:** `/api/v1/favorites/{favorite_id}`
- **Access:** Authenticated (`Authorization: Bearer <token>`)
- **Success Status:** `200 OK`

#### Success Response (`200 OK`)
```json
{
  "success": true,
  "data": {
    "deleted_id": 12,
    "message": "Favorite removed."
  },
  "message": "Removed from favorites successfully."
}
```

#### Error Responses
- **403 Forbidden (`ACCESS_DENIED` / `FORBIDDEN`):** User is not the owner of this favorite.
- **404 Not Found (`RESOURCE_NOT_FOUND`):** Favorite ID does not exist.
