# Bloop — REST API Specification & Contract Reference (v1)

**Document Identifier:** BLOOP-API-V1  
**Project:** Bloop — AI Text-to-Speech & Quantum Intelligence Platform  
**Target Milestone:** Intermediate-Level Architecture  
**Status:** Approved API Reference  
**Authority:** Bloop Master Prompt & Prompt 02  
**Base Path:** `/api/v1`

---

## 1. Standardized JSON Envelope Contract

All endpoints in the Bloop API adhere to a deterministic JSON envelope contract:

### 1.1 Success Response Envelope
```json
{
  "success": true,
  "data": { ... },
  "message": "Human-readable description of the completed operation"
}
```

### 1.2 Error Response Envelope
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Descriptive, human-readable safe message",
    "details": null
  }
}
```

### 1.3 Paginated Response Envelope (under `data`)
```json
{
  "items": [ ... ],
  "total": 42,
  "page": 1,
  "page_size": 10,
  "has_next": true
}
```

---

## 2. API Endpoints Catalog

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             API ENDPOINTS DIRECTORY                         │
├────────────────────┬────────────────────────────────────────────────────────┤
│ Health & Metrics   │ GET /api/v1/health                                     │
│ Authentication     │ POST /api/v1/auth/register, POST /login, GET /me       │
│ Languages & Voices │ GET /api/v1/languages, GET /voices, POST /voices, etc.  │
│ Text-to-Speech     │ POST /api/v1/tts, POST /analyze, GET /audio, /download │
│ History & Favorites│ GET /api/v1/history, DELETE /{id}, GET /favorites, etc.│
│ Quantum Laboratory │ POST /text, POST /emotion, POST /semantic, /circuit... │
└────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 3. Health & System Diagnostics

### `GET /api/v1/health`
Checks backend application health, database connectivity, and provider status. Public endpoint used for Render zero-downtime health probes.

#### Response (200 OK):
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "environment": "production",
    "database": "connected",
    "provider": "elevenlabs"
  },
  "message": "Bloop API is healthy and operational"
}
```

---

## 4. Authentication Endpoints

### `POST /api/v1/auth/register`
Registers a new user account with email and password.

#### Request Body:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "Ada Lovelace"
}
```

#### Response (201 Created):
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "full_name": "Ada Lovelace",
      "is_active": true,
      "created_at": "2026-09-14T11:40:00Z"
    }
  },
  "message": "User registered successfully"
}
```

#### Errors:
* `409 Conflict`: `{"code": "EMAIL_ALREADY_EXISTS", "message": "Email is already registered"}`
* `422 Unprocessable Entity`: `{"code": "VALIDATION_ERROR", "message": "Password must be at least 8 characters"}`

---

### `POST /api/v1/auth/login`
Authenticates user credentials and issues a JWT access token.

#### Request Body:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

#### Response (200 OK):
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "full_name": "Ada Lovelace",
      "is_active": true
    }
  },
  "message": "Login successful"
}
```

#### Errors:
* `401 Unauthorized`: `{"code": "INVALID_CREDENTIALS", "message": "Incorrect email or password"}`

---

### `GET /api/v1/auth/me`
Retrieves current authenticated user profile and preferences. Requires `Authorization: Bearer <token>`.

#### Response (200 OK):
```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "Ada Lovelace",
    "preferences": {
      "default_language": "en-US",
      "default_voice_id": "eleven-voice-1",
      "theme": "dark",
      "playback_speed": 1.0
    }
  }
}
```

---

## 5. Languages & Dynamic Voice Endpoints

### `GET /api/v1/languages`
Lists all active ISO language locales.

#### Response (200 OK):
```json
{
  "success": true,
  "data": [
    {"code": "en-US", "name": "English (US)", "is_active": true},
    {"code": "en-GB", "name": "English (UK)", "is_active": true},
    {"code": "es-ES", "name": "Spanish (Spain)", "is_active": true},
    {"code": "fr-FR", "name": "French (France)", "is_active": true},
    {"code": "de-DE", "name": "German (Germany)", "is_active": true},
    {"code": "hi-IN", "name": "Hindi (India)", "is_active": true}
  ]
}
```

---

### `GET /api/v1/voices`
Retrieves available voices from the dynamic registry with optional filtering.

#### Query Parameters:
* `language_code` (optional, string): e.g. `en-US`
* `gender` (optional, string): `female`, `male`, `neutral`

#### Response (200 OK):
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "voice_id": "21m00Tcm4TlvDq8ikWAM",
      "name": "Rachel (Custom)",
      "language_code": "en-US",
      "gender": "female",
      "provider": "elevenlabs",
      "is_active": true,
      "is_user_configured": true
    }
  ]
}
```

---

### `POST /api/v1/voices`
Injects a user-provided ElevenLabs voice ID into the dynamic voice registry.

#### Request Body:
```json
{
  "voice_id": "21m00Tcm4TlvDq8ikWAM",
  "name": "Rachel",
  "language_code": "en-US",
  "gender": "female",
  "description": "Warm, natural narration voice"
}
```

#### Response (201 Created):
```json
{
  "success": true,
  "data": {
    "id": 12,
    "voice_id": "21m00Tcm4TlvDq8ikWAM",
    "name": "Rachel",
    "language_code": "en-US",
    "is_active": true,
    "is_user_configured": true
  },
  "message": "Custom voice registered successfully"
}
```

---

### `POST /api/v1/voices/reload-config`
Reloads custom voice definitions from `backend/voices_config.json`.

#### Response (200 OK):
```json
{
  "success": true,
  "data": {
    "loaded": 5,
    "updated": 1
  },
  "message": "Voice registry reloaded from configuration file"
}
```

---

## 6. Core Text-to-Speech Endpoints

### `POST /api/v1/tts`
Primary speech synthesis endpoint. Requires `Authorization: Bearer <token>`.

#### Request Body:
```json
{
  "text": "Quantum computing enables superposed state calculations.",
  "language": "en-US",
  "voice_id": "21m00Tcm4TlvDq8ikWAM",
  "speed": 1.0,
  "pitch": 0.0
}
```

#### Response (200 OK):
```json
{
  "success": true,
  "data": {
    "id": 42,
    "audio_url": "/api/v1/tts/audio/bloop-gen-42.mp3",
    "download_url": "/api/v1/tts/download/bloop-gen-42.mp3",
    "duration_seconds": 3.8,
    "character_count": 55,
    "word_count": 7,
    "created_at": "2026-09-14T11:45:00Z"
  },
  "message": "Speech generated successfully"
}
```

#### Errors:
* `400 Bad Request`: `{"code": "EMPTY_TEXT", "message": "Text cannot be empty"}`
* `400 Bad Request`: `{"code": "TEXT_TOO_LONG", "message": "Text exceeds maximum limit of 2,500 characters"}`
* `400 Bad Request`: `{"code": "VOICE_LANGUAGE_MISMATCH", "message": "Voice is incompatible with selected language"}`
* `502 Bad Gateway`: `{"code": "PROVIDER_ERROR", "message": "Speech provider error. Please try again."}`

---

### `POST /api/v1/tts/analyze`
Computes character count, word count, estimated duration, and validity without invoking synthesis.

#### Request Body:
```json
{"text": "Sample text for metrics evaluation."}
```

#### Response (200 OK):
```json
{
  "success": true,
  "data": {
    "character_count": 35,
    "word_count": 5,
    "estimated_duration_seconds": 2.1,
    "is_valid": true,
    "remaining_characters": 2465
  }
}
```

---

### `GET /api/v1/tts/audio/{filename}`
Streams synthesized audio file. Supports HTTP `Range` requests (HTTP 206 Partial Content) for seeking.

#### Headers:
* Request: `Range: bytes=1048576-`
* Response: `Content-Range: bytes 1048576-3145727/3145728`, `Content-Type: audio/mpeg`

---

### `GET /api/v1/tts/download/{filename}`
Serves audio file as a browser download attachment.

#### Headers:
* Response: `Content-Disposition: attachment; filename="bloop-speech-42.mp3"`

---

## 7. Speech History & Favorites Endpoints

### `GET /api/v1/history`
Returns paginated speech generation records for the authenticated user.

#### Query Parameters:
* `page` (int, default: 1)
* `page_size` (int, default: 10)
* `search` (string, optional): Substring filter on text
* `language` (string, optional): Filter by language code
* `voice_id` (string, optional): Filter by voice ID
* `sort` (string, default: `desc`): `asc` or `desc`

#### Response (200 OK):
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 42,
        "text": "Quantum computing enables superposed state calculations.",
        "language_code": "en-US",
        "voice_id": "21m00Tcm4TlvDq8ikWAM",
        "voice_name": "Rachel",
        "duration_seconds": 3.8,
        "character_count": 55,
        "audio_url": "/api/v1/tts/audio/bloop-gen-42.mp3",
        "is_favorited": true,
        "created_at": "2026-09-14T11:45:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 10,
    "has_next": false
  }
}
```

---

### `DELETE /api/v1/history/{id}`
Deletes a generation record and removes the corresponding audio file from disk. Requires ownership.

#### Response (200 OK):
```json
{
  "success": true,
  "message": "Generation record deleted successfully"
}
```

---

### `GET /api/v1/favorites`
Returns all bookmarked generations for the authenticated user with pagination.

---

### `POST /api/v1/favorites`
Bookmarks a speech generation record.

#### Request Body:
```json
{"generation_id": 42}
```

#### Response (201 Created):
```json
{
  "success": true,
  "data": {"id": 8, "generation_id": 42, "favorited": true},
  "message": "Added to favorites"
}
```

---

### `DELETE /api/v1/favorites/{id}`
Removes a bookmark. Requires ownership.

---

## 8. Quantum Intelligence Endpoints

### `POST /api/v1/quantum/text`
Executes Qiskit Aer Variational Quantum Classifier (VQC) with Hilbert angle encoding.

#### Request Body:
```json
{"text": "The theorem proves asymptotic convergence under bounded variance."}
```

#### Response (200 OK):
```json
{
  "success": true,
  "data": {
    "predicted_style": "Technical",
    "probabilities": {
      "Technical": 0.86,
      "Formal": 0.09,
      "Creative": 0.03,
      "Casual": 0.02
    },
    "qubit_angles": [1.42, 0.85, 2.14, 0.44],
    "classical_baseline": {
      "heuristic_style": "Technical",
      "confidence": 0.82
    },
    "execution_time_ms": 145
  }
}
```

---

### `POST /api/v1/quantum/emotion`
Runs PennyLane Hybrid QNN to evaluate affective wire expectation values and entanglement entropy.

#### Request Body:
```json
{"text": "I am thrilled with these extraordinary results!"}
```

#### Response (200 OK):
```json
{
  "success": true,
  "data": {
    "dominant_emotion": "Joy",
    "expectations": {
      "Joy": 0.88,
      "Sadness": -0.82,
      "Anger": -0.75,
      "Neutral": 0.12
    },
    "entanglement_entropy": 1.45,
    "recommended_voice_tuning": {
      "suggested_speed_multiplier": 1.15,
      "suggested_pitch_variance_pct": 12.0,
      "rationale": "High Joy expectation maps to heightened pitch variance and faster cadence."
    }
  }
}
```

---

### `POST /api/v1/quantum/semantic`
Computes Quantum Kernel State Overlap Fidelity $|⟨\phi(A)|\psi(B)⟩|^2$ via state inversion circuits on Qiskit Aer.

#### Request Body:
```json
{
  "text_a": "Understanding quantum circuit logic.",
  "text_b": "Exploring quantum gate mechanics."
}
```

#### Response (200 OK):
```json
{
  "success": true,
  "data": {
    "quantum_fidelity": 0.842,
    "classical_cosine_similarity": 0.795,
    "verdict": "High Semantic Alignment",
    "circuit_shots": 1024
  }
}
```

---

### `POST /api/v1/quantum/circuit`
Interactive circuit sandbox: compiles gates, runs ideal or noisy Aer simulation, and returns ASCII wire diagram and OpenQASM.

#### Request Body:
```json
{
  "qubit_count": 2,
  "gates": [
    {"gate": "H", "target": 0},
    {"gate": "CNOT", "control": 0, "target": 1}
  ],
  "simulate_noise": true,
  "shots": 1024
}
```

#### Response (200 OK):
```json
{
  "success": true,
  "data": {
    "measurement_counts": {"00": 482, "11": 490, "01": 26, "10": 26},
    "measurement_probabilities": {"00": 0.47, "11": 0.48, "01": 0.025, "10": 0.025},
    "ascii_diagram": "q_0: ──H────■──\n     ┌───┐┌─┴─┐\nq_1: ─┤ X ├┤   ├──\n     └───┘└───┘",
    "openqasm": "OPENQASM 2.0;\ninclude \"qelib1.inc\";\nqreg q[2];\ncreg c[2];\nh q[0];\ncx q[0],q[1];\nmeasure q -> c;"
  }
}
```

---

### `POST /api/v1/quantum/benchmark`
Runs an objective empirical benchmark comparing Scikit-Learn Logistic Regression with Qiskit VQC.

#### Request Body:
```json
{
  "dataset_id": "sentiment-standard",
  "shots": 1024
}
```

#### Response (200 OK):
```json
{
  "success": true,
  "data": {
    "classical_metrics": {
      "model": "LogisticRegression (Scikit-Learn)",
      "accuracy": 0.912,
      "f1_score": 0.905,
      "latency_ms": 12.4
    },
    "quantum_metrics": {
      "model": "VariationalQuantumClassifier (Qiskit Aer)",
      "accuracy": 0.864,
      "f1_score": 0.852,
      "latency_ms": 1420.0
    },
    "analysis": "The classical model achieves higher throughput due to CPU matrix math. Quantum VQC provides high-dimensional Hilbert feature separation with simulation latency overhead."
  }
}
```
