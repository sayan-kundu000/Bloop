# Bloop REST API — Generation History Specification

## 1. Overview & Resource Ownership Boundary

The **History Domain** tracks the audit trail of all speech synthesis requests. Strict tenant and user isolation rules are enforced:
- **Ownership Isolation:** Authenticated users only see and manipulate generation records linked to their `user_id`. Superusers possess cross-tenant administrative visibility.
- **Unauthorized Access Denial:** Attempting to retrieve (`GET /history/{id}`) or delete (`DELETE /history/{id}`) another user's generation returns `403 Forbidden` (`ACCESS_DENIED` / `FORBIDDEN`).

---

## 2. Endpoints

### 2.1 List Generation History (Paginated)

Retrieves a paginated list of generation records matching optional search, language, and sorting parameters.

- **Method:** `GET`
- **Path:** `/api/v1/history`
- **Access:** Authenticated (`Authorization: Bearer <token>`)
- **Success Status:** `200 OK`

#### Query Parameters

| Parameter | Type | Default | Constraints | Description |
| :--- | :--- | :--- | :--- | :--- |
| `search` | `string` | `None` | Max 100 chars | Keyword search in text content and voice name |
| `language` | `string` | `None` | Max 10 chars | Filter by BCP-47 locale code |
| `sort_by` | `string` | `"created_at"`| `created_at`, `duration_seconds`, `char_count` | Sort attribute |
| `order` | `string` | `"desc"` | `"asc"` or `"desc"` | Sort direction |
| `page` | `integer`| `1` | `>= 1` | 1-indexed page number |
| `page_size`| `integer`| `20` | `1 <= x <= 100` | Records per page |

#### Response (`ApiResponse[PaginatedResponse[HistoryItemResponse]]`)
```json
{
  "success": true,
  "data": {
    "items": [
      {
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
        "is_favorite": false,
        "favorite_id": null,
        "created_at": "2026-09-17T18:10:00Z"
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
  "message": "Speech generation history retrieved."
}
```

---

### 2.2 Get Single Generation Record

Fetches a single generation record by its ID with ownership validation.

- **Method:** `GET`
- **Path:** `/api/v1/history/{generation_id}`
- **Access:** Authenticated (`Authorization: Bearer <token>`)
- **Success Status:** `200 OK`

#### Success Response (`ApiResponse[HistoryItemResponse]`)
```json
{
  "success": true,
  "data": {
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
  },
  "message": "Generation record retrieved."
}
```

#### Error Responses
- **403 Forbidden (`ACCESS_DENIED` / `FORBIDDEN`):** Record belongs to another user.
- **404 Not Found (`RESOURCE_NOT_FOUND`):** Generation record ID does not exist.

---

### 2.3 Delete Generation Record

Removes a generation record and invalidates associated audio files.

- **Method:** `DELETE`
- **Path:** `/api/v1/history/{generation_id}`
- **Access:** Authenticated (`Authorization: Bearer <token>`)
- **Success Status:** `200 OK`

#### Success Response (`200 OK`)
```json
{
  "success": true,
  "data": {
    "deleted_id": 142,
    "message": "Generation record deleted."
  },
  "message": "Generation record deleted successfully."
}
```

#### Error Responses
- **403 Forbidden (`ACCESS_DENIED` / `FORBIDDEN`):** User is not the owner of the record.
- **404 Not Found (`RESOURCE_NOT_FOUND`):** Record does not exist.
