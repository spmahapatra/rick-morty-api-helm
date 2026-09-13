# Architecture Overview

## Project Structure

The Rick and Morty API project is a Python-based REST API service that fetches character data from an external API and provides caching, structured logging, and comprehensive error handling.

## System Components

### 1. **API Layer** (`app.py`)
- **Purpose**: Main Flask application entry point
- **Responsibilities**:
  - Handle HTTP requests and route them to appropriate endpoints
  - Manage request/response lifecycle
  - Implement CORS and security headers
  - Serve health check endpoint
- **Key Endpoints**:
  - `GET /health` - Service health status
  - `GET /characters/<id>` - Fetch character by ID
  - `GET /characters/search` - Search characters by name
  - `POST /cache/flush` - Clear cache
  - `GET /cache/stats` - View cache statistics

### 2. **Cache Layer** (`src/cache/`)
- **Purpose**: Optimize API response times through intelligent caching
- **Components**:
  - `detection.py` - Cache hit/miss detection logic
  - `middleware.py` - WSGI middleware for transparent caching
  - `backend.py` - Redis cache backend implementation
- **Architecture**:
  - Request-based cache key generation
  - Automatic cache population on external API calls
  - TTL-based expiration (configurable, default 3600s)
  - Cache statistics tracking

### 3. **Database Layer** (`src/db/`)
- **Purpose**: Persist character data and system information
- **Technology**: PostgreSQL
- **Schema**:
  - `characters` table - Character metadata
  - `api_calls` table - API call history and metrics
  - `cache_events` table - Cache hit/miss tracking
  - `system_logs` table - Application event logging
- **Connection Management**:
  - Connection pooling via SQLAlchemy
  - Automatic reconnection with exponential backoff
  - Health check validation

### 4. **Logging Layer** (`src/logging/`)
- **Purpose**: Structured, traceable application logging
- **Features**:
  - JSON-formatted output for machine parsing
  - Correlation IDs for request tracing across services
  - Structured context injection (user, request ID, etc.)
  - Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Output**: Stdout (JSON) for containerized environments

### 5. **Configuration Management** (`config.py`)
- **Purpose**: Centralized configuration handling
- **Environment Support**:
  - Development (local, debug enabled)
  - Production (remote services, security hardened)
- **Configuration Sources**:
  - Environment variables
  - `.env` file (development)
  - Defaults with validation

### 6. **External Integration** (`src/api/`)
- **Purpose**: Communication with Rick & Morty public API
- **Implementation**:
  - HTTP client with retry logic
  - Timeout handling
  - Error propagation

## Data Flow

### Request Processing Flow

```
Client Request
     ↓
Flask Router (app.py)
     ↓
Cache Middleware (detection.py)
     ↓
Cache Hit? → Return cached response
     ↓
Cache Miss
     ↓
External API Call (src/api/)
     ↓
Store in Database (src/db/)
     ↓
Store in Redis Cache (src/cache/)
     ↓
Structured Logging (src/logging/)
     ↓
Return Response
```

### Logging Flow

```
Request Context Established (correlation_id)
     ↓
Context Injection into Thread-Local Storage
     ↓
Logging Handler Captures Context
     ↓
JSON Serialization
     ↓
Stdout Output
```

## Deployment Architecture

### Docker Composition

- **API Container**: Python application with Flask
- **PostgreSQL Container**: Persistent data storage
- **Redis Container**: In-memory cache backend
- **Network**: Bridge network for inter-container communication

### Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `FLASK_ENV` | Execution environment | `production` |
| `REDIS_URL` | Redis connection | `redis://redis:6379/0` |
| `DATABASE_URL` | PostgreSQL connection | `postgresql://user:pass@postgres:5432/rickmorty` |
| `CACHE_TTL` | Cache expiration time (seconds) | `3600` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |

## Security Considerations

1. **Input Validation**: All user inputs validated before processing
2. **Error Handling**: Sensitive information excluded from error responses
3. **CORS**: Restricted to configured origins
4. **Database**: Connection uses secure credentials
5. **Logging**: No sensitive data logged to persistent storage

## Performance Characteristics

### Caching Impact
- **Cache Hit Response Time**: 150-200ms (Redis backend)
- **Cache Miss Response Time**: 270-300ms (external API + overhead)
- **Performance Improvement**: ~50% reduction on cache hits

### Database Performance
- **Connection Pool Size**: 10 connections (configurable)
- **Query Timeout**: 30 seconds
- **Automatic Cleanup**: Connection recycling every 3600s

## Scalability Considerations

1. **Horizontal Scaling**: Stateless API allows multiple instances
2. **Cache Distribution**: Redis backend supports clustering
3. **Database**: PostgreSQL connection pooling for multiple API instances
4. **Load Balancing**: Deploy behind load balancer for traffic distribution

## Monitoring & Observability

### Health Checks
- API health endpoint: `GET /health`
- Database connectivity validation
- Redis connectivity validation
- External API reachability

### Metrics Available
- Cache hit/miss ratio
- API response times
- Database query performance
- Error rates by type

### Logging Output
- Structured JSON logs with correlation IDs
- Request/response tracing
- Performance metrics
- Error stack traces (development only)

## Future Enhancements

1. **Authentication**: JWT-based API authentication
2. **Rate Limiting**: Request throttling per client
3. **Metrics Export**: Prometheus-compatible endpoint
4. **Circuit Breaker**: Resilience pattern for external API
5. **Distributed Tracing**: Full observability with OpenTelemetry
