# Bloop REST API — Users & Preferences Specification

## 1. Overview

The **Users Domain** provides endpoints for viewing and modifying personal profile data and speech synthesis workstation preferences. All routes require an active JWT Bearer token and enforce strict user isolation: a user can only inspect or modify their own profile record.

---

## 2. Endpoints

### 2.1 Get Current User Profile & Preferences

Returns full user profile details, including the attached synthesis preferences record.

- **Method:** `GET`
- **Path:** `/api/v1/users/me`
- **Access:** Authenticated (`Authorization: Bearer <token>`)
- **Success Status:** `200 OK`

#### Response (`UserWithPreferencesResponse`)
```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "developer@bloop.ai",
    "full_name": "Bloop Developer",
    "is_active": true,
    "is_superuser": false,
    "created_at": "2026-09-17T18:00:00Z",
    "preference": {
      "id": 1,
      "user_id": 1,
      "theme": "dark",
      "default_voice_id": null,
      "default_language": "en-US",
      "audio_speed": 1.0,
      "auto_play": false,
      "updated_at": "2026-09-17T18:00:00Z"
    }
  },
  "message": "User profile retrieved successfully."
}
```

---

### 2.2 Update User Profile

Allows updating personal details, including full name, email address, or password.

- **Method:** `PATCH`
- **Path:** `/api/v1/users/me`
- **Access:** Authenticated (`Authorization: Bearer <token>`)
- **Success Status:** `200 OK`

#### Request Payload (`UserUpdate`)
```json
{
  "full_name": "Senior Bloop Engineer",
  "email": "senior@bloop.ai"
}
```

| Field | Type | Required | Constraints | Description |
| :--- | :--- | :--- | :--- | :--- |
| `full_name` | `string` | No | Max 100 chars | New display name |
| `email` | `string` | No | Valid email | New primary email address |
| `password` | `string` | No | Min 8 chars | New password (will be re-hashed) |

#### Success Response (`200 OK`)
```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "senior@bloop.ai",
    "full_name": "Senior Bloop Engineer",
    "is_active": true,
    "is_superuser": false,
    "created_at": "2026-09-17T18:00:00Z"
  },
  "message": "User profile updated successfully."
}
```

#### Error Responses
- **409 Conflict (`RESOURCE_CONFLICT`):** Requested email is already taken by another account.
- **422 Unprocessable Entity (`VALIDATION_ERROR`):** Password length < 8 chars or invalid email syntax.

---

### 2.3 Get User Preferences

Retrieves the standalone preferences object for the current user.

- **Method:** `GET`
- **Path:** `/api/v1/users/me/preferences`
- **Access:** Authenticated (`Authorization: Bearer <token>`)
- **Success Status:** `200 OK`

#### Response (`UserPreferenceResponse`)
```json
{
  "success": true,
  "data": {
    "id": 1,
    "user_id": 1,
    "theme": "dark",
    "default_voice_id": null,
    "default_language": "en-US",
    "audio_speed": 1.0,
    "auto_play": false,
    "updated_at": "2026-09-17T18:00:00Z"
  },
  "message": "User preferences retrieved successfully."
}
```

---

### 2.4 Update User Preferences

Modifies UI workstation settings, default voice and language preferences, and audio playback characteristics.

- **Method:** `PATCH`
- **Path:** `/api/v1/users/me/preferences`
- **Access:** Authenticated (`Authorization: Bearer <token>`)
- **Success Status:** `200 OK`

#### Request Payload (`UserPreferenceUpdate`)
```json
{
  "theme": "dark",
  "default_language": "en-US",
  "default_voice_id": "sim_voice_warm",
  "audio_speed": 1.25,
  "auto_play": true
}
```

| Field | Type | Required | Constraints | Description |
| :--- | :--- | :--- | :--- | :--- |
| `theme` | `string` | No | `"light"` or `"dark"` | UI theme mode |
| `default_language` | `string` | No | Max 10 chars | Default BCP-47 locale |
| `default_voice_id` | `string` | No | Max 50 chars | Preferred voice identifier |
| `audio_speed` | `float` | No | `0.5 <= x <= 2.0` | Playback speed multiplier |
| `auto_play` | `boolean` | No | Boolean | Automatically play generated speech |

#### Success Response (`200 OK`)
```json
{
  "success": true,
  "data": {
    "id": 1,
    "user_id": 1,
    "theme": "dark",
    "default_voice_id": "sim_voice_warm",
    "default_language": "en-US",
    "audio_speed": 1.25,
    "auto_play": true,
    "updated_at": "2026-09-17T18:05:00Z"
  },
  "message": "User preferences updated successfully."
}
```
