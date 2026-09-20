# Bloop REST API — Authentication Specification

## 1. Overview

The **Authentication Domain** manages identity registration, credential verification, and cryptographic JSON Web Token (JWT) issuance. Bloop uses HMAC-SHA256 signed Bearer tokens containing user identification claims, validated on protected routes via FastAPI dependency injection (`get_current_user`).

---

## 2. Endpoints

### 2.1 Register New Account

Creates a new user account, provisions default synthesis preferences (`theme="dark"`, `audio_speed=1.0`, `auto_play=false`), hashes credentials using `bcrypt`, and immediately returns an active access token.

- **Method:** `POST`
- **Path:** `/api/v1/auth/register`
- **Access:** Public
- **Success Status:** `201 Created`

#### Request Payload (`RegisterRequest`)
```json
{
  "email": "developer@bloop.ai",
  "password": "SecurePassword123!",
  "full_name": "Bloop Developer"
}
```

| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `email` | `string` | Email format, max 255 | Unique user email address |
| `password` | `string` | Min 8 chars, max 100 | Cleartext password to hash |
| `full_name`| `string` | Optional, max 100 | Optional human display name |

#### Success Response (`201 Created`)
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 86400,
    "user": {
      "id": 1,
      "email": "developer@bloop.ai",
      "full_name": "Bloop Developer",
      "is_active": true,
      "is_superuser": false,
      "created_at": "2026-09-17T18:00:00Z"
    }
  },
  "message": "Registration successful."
}
```

#### Error Responses
- **409 Conflict (`RESOURCE_CONFLICT` / `CONFLICT`):** Email address is already registered.
- **422 Unprocessable Entity (`VALIDATION_ERROR`):** Password length < 8 chars or invalid email syntax.

---

### 2.2 User Login

Authenticates email and password credentials, returning a signed JWT access token.

- **Method:** `POST`
- **Path:** `/api/v1/auth/login`
- **Access:** Public
- **Success Status:** `200 OK`

#### Request Payload (`LoginRequest`)
```json
{
  "email": "developer@bloop.ai",
  "password": "SecurePassword123!"
}
```

#### Success Response (`200 OK`)
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 86400,
    "user": {
      "id": 1,
      "email": "developer@bloop.ai",
      "full_name": "Bloop Developer",
      "is_active": true,
      "is_superuser": false,
      "created_at": "2026-09-17T18:00:00Z"
    }
  },
  "message": "Login successful."
}
```

#### Error Responses
- **401 Unauthorized (`INVALID_CREDENTIALS`):** Incorrect email or password.
- **422 Unprocessable Entity (`VALIDATION_ERROR`):** Malformed request body.

---

### 2.3 User Logout

Signals client session termination and client-side token discard.

- **Method:** `POST`
- **Path:** `/api/v1/auth/logout`
- **Access:** Public / Authenticated
- **Success Status:** `200 OK`

#### Response (`LogoutResponse`)
```json
{
  "success": true,
  "data": {
    "logged_out": true,
    "message": "User session terminated."
  },
  "message": "Logged out successfully."
}
```

---

### 2.4 Current User Profile (Auth Module)

Retrieves identity details of the token bearer.

- **Method:** `GET`
- **Path:** `/api/v1/auth/me`
- **Access:** Authenticated (`Authorization: Bearer <token>`)
- **Success Status:** `200 OK`

#### Success Response (`200 OK`)
```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "developer@bloop.ai",
    "full_name": "Bloop Developer",
    "is_active": true,
    "is_superuser": false,
    "created_at": "2026-09-17T18:00:00Z"
  },
  "message": "Current user profile retrieved."
}
```

#### Error Responses
- **401 Unauthorized (`AUTHENTICATION_REQUIRED` / `AUTHENTICATION_FAILED`):** Missing, invalid, or expired Bearer token.
