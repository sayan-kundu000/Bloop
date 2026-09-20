# Bloop REST API — Languages Domain Specification

## 1. Overview

The **Languages Domain** provides read access to the catalog of supported linguistic locales recognized by Bloop. All locales conform to standardized BCP-47 / ISO 639-1 language tags and associate dynamically with synthetic voices via direct locale keys and many-to-many capability mappings.

---

## 2. Endpoints

### 2.1 List Supported Languages

Retrieves the complete catalog of active languages supported by the synthesis engine, including localized native names, text direction (`ltr`/`rtl`), and optional locale metadata.

- **Method:** `GET`
- **Path:** `/api/v1/languages`
- **Access:** Public (No authentication required)
- **Success Status:** `200 OK`

#### Response (`ApiResponse[List[LanguageResponse]]`)
```json
{
  "success": true,
  "data": [
    {
      "code": "en-US",
      "name": "English (US)",
      "native_name": "English",
      "direction": "ltr",
      "is_active": true,
      "metadata": null
    },
    {
      "code": "es-ES",
      "name": "Spanish (Spain)",
      "native_name": "Español",
      "direction": "ltr",
      "is_active": true,
      "metadata": null
    }
  ],
  "message": "Languages retrieved successfully"
}
```

#### Empty Catalog Response
If no languages are currently configured or active, the API returns:
```json
{
  "success": true,
  "data": [],
  "message": "Languages retrieved successfully"
}
```

---

### 2.2 Get Language by Code

Retrieves metadata for a specific language locale.

- **Method:** `GET`
- **Path:** `/api/v1/languages/{code}`
- **Access:** Public
- **Success Status:** `200 OK`

#### Success Response (`ApiResponse[LanguageResponse]`)
```json
{
  "success": true,
  "data": {
    "code": "en-US",
    "name": "English (US)",
    "native_name": "English",
    "direction": "ltr",
    "is_active": true,
    "metadata": null
  },
  "message": "Language retrieved successfully"
}
```

#### Error Response (404 Not Found)
```json
{
  "success": false,
  "error": {
    "code": "LANGUAGE_NOT_FOUND",
    "message": "Language 'xx-YY' not found or inactive",
    "details": {}
  }
}
```

---

## 3. Schema Definitions

### `LanguageResponse`
| Field | Type | Description |
| :--- | :--- | :--- |
| `code` | `string` | BCP-47 locale identifier (e.g. `en-US`, `es-ES`) |
| `name` | `string` | Internationalized English name |
| `native_name` | `string` (nullable) | Native script representation (e.g. `हिन्दी`, `日本語`) |
| `direction` | `string` | Text layout direction: `'ltr'` (left-to-right) or `'rtl'` (right-to-left) |
| `is_active` | `boolean` | Synthesis availability flag |
| `metadata` | `object` (nullable) | Extensible script and dialect metadata |
