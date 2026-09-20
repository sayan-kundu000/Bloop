# Bloop REST API — Pagination & Collection Specification

## 1. Overview & Dual-Layer Pagination Model

Bloop utilizes a **dual-layer pagination structure** across all collection endpoints (such as `/api/v1/history` and `/api/v1/favorites`). This design provides both self-contained collection payloads in `data` and top-level pagination metadata in `meta` for seamless frontend state integration (e.g. TanStack Query).

---

## 2. Standard Envelope Structure

```json
{
  "success": true,
  "data": {
    "items": [ /* array of resource items */ ],
    "total": 142,
    "page": 1,
    "page_size": 20,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  },
  "meta": {
    "page": 1,
    "page_size": 20,
    "total": 142,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  },
  "message": "Resource collection retrieved successfully."
}
```

---

## 3. Query Parameters & Constraints

| Parameter | Type | Default | Constraints | Description |
| :--- | :--- | :--- | :--- | :--- |
| `page` | `integer` | `1` | `ge=1` | 1-indexed page pointer |
| `page_size` | `integer` | `20` | `ge=1, le=100` | Number of items per page (capped at 100) |

If an invalid page or size is provided (e.g., `page_size=500` or `page=0`), FastAPI rejects the request with HTTP `422 Unprocessable Entity` before reaching the database.

---

## 4. Derived Field Calculations

- **`total_pages`**: `ceil(total / page_size)` (or `1` if `total == 0`)
- **`has_next`**: `(page * page_size) < total`
- **`has_prev`**: `page > 1`

---

## 5. Frontend TanStack Query Integration Example

```typescript
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

export interface HistoryItem {
  id: number;
  text: string;
  voice_name: string;
  created_at: string;
}

export interface PaginatedHistoryResponse {
  success: boolean;
  data: {
    items: HistoryItem[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
  meta: {
    page: number;
    page_size: number;
    total: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
}

export function useHistory(page = 1, pageSize = 20) {
  return useQuery({
    queryKey: ['history', page, pageSize],
    queryFn: async () => {
      const response = await axios.get<PaginatedHistoryResponse>(
        `/api/v1/history?page=${page}&page_size=${pageSize}`
      );
      return response.data;
    },
    keepPreviousData: true,
  });
}
```
