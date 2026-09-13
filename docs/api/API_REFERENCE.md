# API Reference

## Base URL

```
http://localhost:5000
```

## Authentication

Currently, no authentication is required. All endpoints are publicly accessible within your network.

**Future Versions**: JWT-based authentication will be implemented for production deployments.

## Response Format

All responses are in JSON format with the following structure:

### Success Response (2xx)
```json
{
  "status": "success",
  "data": { /* resource data */ },
  "timestamp": "2026-09-13T16:01:00Z",
  "correlation_id": "req_abc123xyz"
}
```

### Error Response (4xx, 5xx)
```json
{
  "status": "error",
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Character with ID 999 not found",
    "details": null
  },
  "timestamp": "2026-09-13T16:01:00Z",
  "correlation_id": "req_abc123xyz"
}
```

## Endpoints

### Health Check

#### GET /health
Check if the API service is running and all dependencies are healthy.

**Response**: 200 OK
```json
{
  "status": "healthy",
  "timestamp": "2026-09-13T16:01:00Z",
  "checks": {
    "database": "connected",
    "redis": "connected",
    "external_api": "reachable"
  }
}
```

---

### Characters

#### GET /characters/<id>
Fetch a single character by ID.

**Parameters**:
- `id` (path, required): Character ID (integer)

**Response**: 200 OK
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "name": "Rick Sanchez",
    "status": "Alive",
    "species": "Human",
    "type": "",
    "gender": "Male",
    "origin": {
      "name": "Earth",
      "url": "https://rickandmortyapi.com/api/location/1"
    },
    "location": {
      "name": "Earth",
      "url": "https://rickandmortyapi.com/api/location/20"
    },
    "image": "https://raw.githubusercontent.com/...",
    "episode": ["https://rickandmortyapi.com/api/episode/1"],
    "url": "https://rickandmortyapi.com/api/character/1",
    "created": "2017-11-04T18:48:46.250Z"
  },
  "timestamp": "2026-09-13T16:01:00Z",
  "correlation_id": "req_abc123xyz",
  "cache": {
    "hit": false,
    "ttl": 3600
  }
}
```

**Error Responses**:
- 404 Not Found - Character ID not found in external API
- 503 Service Unavailable - Cache or database unavailable
- 504 Gateway Timeout - External API timeout

**Example Request**:
```bash
curl -s http://localhost:5000/characters/1
```

---

#### GET /characters/search?name=<name>
Search for characters by name (partial match).

**Query Parameters**:
- `name` (required): Character name (string, case-insensitive)
- `limit` (optional): Maximum results (default: 10, max: 50)
- `offset` (optional): Result offset for pagination (default: 0)

**Response**: 200 OK
```json
{
  "status": "success",
  "data": {
    "results": [
      {
        "id": 1,
        "name": "Rick Sanchez",
        "status": "Alive",
        "species": "Human",
        /* ... other fields ... */
      },
      {
        "id": 2,
        "name": "Morty Smith",
        "status": "Alive",
        "species": "Human",
        /* ... other fields ... */
      }
    ],
    "total": 2,
    "limit": 10,
    "offset": 0
  },
  "timestamp": "2026-09-13T16:01:00Z",
  "correlation_id": "req_abc123xyz"
}
```

**Error Responses**:
- 400 Bad Request - Invalid query parameters
- 503 Service Unavailable - Cache or database unavailable

**Example Request**:
```bash
curl -s 'http://localhost:5000/characters/search?name=rick&limit=5'
```

---

### Cache Management

#### POST /cache/flush
Clear all cached data.

**Response**: 200 OK
```json
{
  "status": "success",
  "data": {
    "cleared": true,
    "keys_removed": 42,
    "timestamp": "2026-09-13T16:01:00Z"
  },
  "timestamp": "2026-09-13T16:01:00Z",
  "correlation_id": "req_abc123xyz"
}
```

**Error Responses**:
- 503 Service Unavailable - Redis unavailable

**Example Request**:
```bash
curl -X POST http://localhost:5000/cache/flush
```

---

#### GET /cache/stats
View current cache statistics and performance metrics.

**Response**: 200 OK
```json
{
  "status": "success",
  "data": {
    "total_requests": 1250,
    "cache_hits": 875,
    "cache_misses": 375,
    "hit_rate": 0.7,
    "avg_response_time_hit_ms": 175,
    "avg_response_time_miss_ms": 290,
    "cached_keys": 42,
    "cache_size_bytes": 524288,
    "ttl_seconds": 3600
  },
  "timestamp": "2026-09-13T16:01:00Z",
  "correlation_id": "req_abc123xyz"
}
```

**Error Responses**:
- 503 Service Unavailable - Redis unavailable

**Example Request**:
```bash
curl -s http://localhost:5000/cache/stats
```

---

## Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | Request successful, data returned |
| 201 | Created | Resource created (future feature) |
| 204 | No Content | Request successful, no data to return |
| 400 | Bad Request | Invalid parameters or malformed request |
| 401 | Unauthorized | Authentication required (future) |
| 403 | Forbidden | Insufficient permissions (future) |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded (future) |
| 500 | Internal Server Error | Server error (see logs) |
| 503 | Service Unavailable | Cache or database unavailable |
| 504 | Gateway Timeout | External API timeout |

## Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `INVALID_PARAMETER` | Query parameter validation failed | 400 |
| `RESOURCE_NOT_FOUND` | Character or resource not found | 404 |
| `DATABASE_ERROR` | Database connection or query failed | 503 |
| `CACHE_ERROR` | Cache backend unavailable | 503 |
| `EXTERNAL_API_ERROR` | Rick & Morty API error | 502/504 |
| `INTERNAL_ERROR` | Unexpected server error | 500 |

## Rate Limiting (Future)

Rate limiting will be implemented in v2.0:
- **Standard**: 1000 requests per hour per IP
- **Authenticated**: 10000 requests per hour per API key
- **Headers**:
  - `X-RateLimit-Limit`: Total requests allowed
  - `X-RateLimit-Remaining`: Requests remaining
  - `X-RateLimit-Reset`: Unix timestamp of rate limit reset

## Pagination (Future)

Search endpoints will support cursor-based pagination:
- `limit`: Items per page (default: 20, max: 100)
- `offset`: Number of items to skip (default: 0)
- `cursor`: Opaque token for next page (future)

## Versioning

Current API Version: **1.0**

Future versions will be accessed via `/api/v2/` prefix.

Backward compatibility will be maintained for at least 2 major versions.
