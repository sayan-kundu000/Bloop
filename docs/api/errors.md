# Bloop REST API — Error Handling & Taxonomy Specification

## 1. Overview & Security Architecture

Bloop enforces a centralized, predictable error handling contract across all REST endpoints. No raw exception traces, internal SQL statements, database table names, or vendor API credentials are ever exposed in client-facing responses.

---

## 2. Standard Error Envelope

All HTTP 4xx and 5xx responses conform to the following schema:

```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_CONFLICT",
    "message": "Speech generation record is already in your favorites.",
    "details": {
      "generation_id": 142
    }
  }
}
```

| Field | Type | Description |
| :--- | :--- | :--- |
| `success` | `boolean` | Always `false` on error responses |
| `error.code` | `string` | Machine-readable `UPPERCASE_SNAKE_CASE` identifier |
| `error.message` | `string` | Sanitized human-readable description |
| `error.details` | `object` | Contextual diagnostic parameters (safe for client inspection) |

---

## 3. Error Code Taxonomy & HTTP Status Mapping

| HTTP Status | Primary Error Code | Alias / Secondary Code | Trigger Scenario |
| :--- | :--- | :--- | :--- |
| **400 Bad Request** | `BAD_REQUEST` | `INVALID_PARAMETER` | Malformed request parameters or syntax |
| **401 Unauthorized** | `AUTHENTICATION_REQUIRED` | `AUTHENTICATION_FAILED` | Missing or invalid Bearer token |
| **401 Unauthorized** | `INVALID_CREDENTIALS` | — | Incorrect email or password on login |
| **403 Forbidden** | `ACCESS_DENIED` | `FORBIDDEN` | Insufficient permissions or accessing another tenant's resource |
| **404 Not Found** | `RESOURCE_NOT_FOUND` | — | Target entity ID does not exist |
| **409 Conflict** | `RESOURCE_CONFLICT` | `CONFLICT` | Email already registered or duplicate favorite |
| **422 Unprocessable** | `VALIDATION_ERROR` | — | Malformed request structure or invalid parameter types |
| **422 Unprocessable** | `TEXT_EMPTY` | — | Submitted text is empty, null, or solely whitespace |
| **422 Unprocessable** | `TEXT_TOO_LONG` | — | Submitted text exceeds `MAX_TEXT_CHARACTERS` limit |
| **422 Unprocessable** | `INVALID_LANGUAGE` | — | Selected language locale is not registered or inactive |
| **422 Unprocessable** | `INVALID_VOICE` | — | Selected voice is not found or inactive |
| **422 Unprocessable** | `VOICE_LANGUAGE_MISMATCH` | — | Selected voice does not support the requested language locale |
| **429 Too Many Req** | `RATE_LIMIT_EXCEEDED` | — | Client exceeded IP or user quota |
| **500 Internal Error** | `INTERNAL_SERVER_ERROR`| `DATABASE_ERROR` | Unhandled server error (sanitized message emitted) |
| **502 Bad Gateway** | `TTS_PROVIDER_UNAVAILABLE` | `PROVIDER_ERROR` | Third-party provider failure or timeout |
| **503 Unavailable** | `QUANTUM_DISABLED` | `SERVICE_UNAVAILABLE` | Quantum subsystem disabled or temporarily offline |


---

## 4. Production Sanitization Guarantees

1. **SQLAlchemy & Database Exceptions:** In production, internal database errors are logged with full traces to server-side logs (`bloop.log`), while the client receives a generic:
   ```json
   {
     "success": false,
     "error": {
       "code": "DATABASE_ERROR",
       "message": "A database persistence error occurred. Operation was safely rolled back.",
       "details": {}
     }
   }
   ```
2. **Unhandled Python Exceptions:** Handled by the root Starlette exception handler, returning `INTERNAL_SERVER_ERROR` and a safe message.
3. **Secret Masking:** Environment variables, API keys (`ELEVENLABS_API_KEY`, `JWT_SECRET_KEY`), and database connection strings are masked in logs and never serialized to error payloads.
