# API Documentation

This directory contains complete REST API documentation, endpoint specifications, and usage guidelines.

## Contents

### API Reference
📄 **[`API_REFERENCE.md`](API_REFERENCE.md)**
- Complete REST API endpoint documentation
- Request/response formats
- Status and error codes
- Example curl commands
- Rate limiting and versioning

### Endpoints Documentation
📄 **[`ENDPOINTS.md`](ENDPOINTS.md)** *(Coming Soon)*
- Individual endpoint specifications
- Path parameters and query strings
- Request/response schemas
- Real-world examples

### Authentication & Security
📄 **[`AUTHENTICATION.md`](AUTHENTICATION.md)** *(Coming Soon)*
- API key management
- JWT authentication (future)
- OAuth integration (future)
- Security best practices

### Error Handling
📄 **[`ERROR_HANDLING.md`](ERROR_HANDLING.md)** *(Coming Soon)*
- Error response formats
- Error codes and meanings
- Retry strategies
- Troubleshooting common errors

---

## Quick Links

| Need | Document |
|------|----------|
| API overview | `API_REFERENCE.md` |
| Endpoint details | `ENDPOINTS.md` |
| Authentication | `AUTHENTICATION.md` |
| Error codes | `ERROR_HANDLING.md` |

---

## Current Endpoints

### Health & Status
- `GET /health` - Service health check

### Characters (Main API)
- `GET /characters/<id>` - Get character by ID
- `GET /characters/search?name=<name>` - Search characters

### Cache Management
- `GET /cache/stats` - Cache statistics
- `POST /cache/flush` - Clear cache

For details, see `API_REFERENCE.md`

---

## Versioning

**Current Version**: v1.0

API versioning via URL prefix (future):
- Current: `/` (v1.0)
- Future: `/api/v2/` (v2.0)

---

## Response Format

All responses follow a standard JSON envelope:

### Success (2xx)
```json
{
  "status": "success",
  "data": { /* resource */ },
  "timestamp": "2026-09-13T16:01:00Z",
  "correlation_id": "req_abc123xyz"
}
```

### Error (4xx, 5xx)
```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": null
  },
  "timestamp": "2026-09-13T16:01:00Z",
  "correlation_id": "req_abc123xyz"
}
```

---

## Common Use Cases

### Get a Character
```bash
curl http://localhost:5000/characters/1 | jq '.'
```

### Search Characters
```bash
curl 'http://localhost:5000/characters/search?name=rick&limit=5'
```

### Check Service Health
```bash
curl http://localhost:5000/health
```

### View Cache Stats
```bash
curl http://localhost:5000/cache/stats
```

---

## Rate Limiting (Future)

API v2.0 will include rate limiting:
- Standard: 1000 req/hour
- Authenticated: 10000 req/hour

See `AUTHENTICATION.md` for details (when available)

---

## Related Documentation

- **Architecture**: See [`docs/architecture/`](../architecture/) for system design
- **Examples**: See [`docs/examples/`](../examples/) for code samples
- **Operations**: See [`docs/operations/`](../operations/) for monitoring

---

## In This Directory

```
api/
├── README.md (this file)
├── API_REFERENCE.md
├── ENDPOINTS.md (coming soon)
├── AUTHENTICATION.md (coming soon)
└── ERROR_HANDLING.md (coming soon)
```

## Status

| Document | Status |
|----------|--------|
| API_REFERENCE | ✅ Complete |
| ENDPOINTS | 🟡 Planned |
| AUTHENTICATION | 🟡 Planned |
| ERROR_HANDLING | 🟡 Planned |
