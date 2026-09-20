# Bloop — REST API Specification & Developer Guide

The Bloop REST API is exposed under the versioned namespace `/api/v1/`. It follows strict RESTful conventions, utilizing standard JSON envelopes, Bearer JWT authorization, and Pydantic v2 schemas.

## Documentation Endpoints
- **Interactive Swagger UI:** `http://localhost:8000/docs` (or `https://bloop-backend.onrender.com/docs`)
- **ReDoc Technical Reference:** `http://localhost:8000/redoc`
- **OpenAPI 3.1 JSON Specification:** `http://localhost:8000/openapi.json`
- **Detailed Markdown Specification:** [API Architecture Document](../architecture/api-architecture.md) and [Full API Reference](../API_DOCUMENTATION.md)

## Standard Response Envelopes

### Success Envelope
```json
{
  "success": true,
  "data": { ... }
}
```

### Paginated Envelope
```json
{
  "success": true,
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 142,
    "total_pages": 8
  }
}
```

### Error Envelope
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable description",
    "details": { ... }
  }
}
```

## Postman Collection
A complete Postman collection covering all endpoints is available in [`postman/`](../../postman/).
