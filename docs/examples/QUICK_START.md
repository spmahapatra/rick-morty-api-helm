# Quick Start Guide

Get the Rick and Morty API running in 5 minutes!

## Option 1: Docker Compose (Recommended)

### Prerequisites
- Docker and Docker Compose installed
- 5 minutes

### Steps

1. **Clone and Navigate**
   ```bash
   git clone <repository-url>
   cd setupAppCreDepHelmPkg
   ```

2. **Start Services**
   ```bash
   docker-compose up -d
   ```

3. **Verify Health**
   ```bash
   curl http://localhost:5000/health
   ```

4. **Test API**
   ```bash
   curl http://localhost:5000/characters/1
   ```

**Done!** API is running at `http://localhost:5000`

---

## Option 2: Local Development

### Prerequisites
- Python 3.9+
- PostgreSQL
- Redis
- 10 minutes

### Steps

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd setupAppCreDepHelmPkg
   ```

2. **Setup Python Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database and Redis URLs
   ```

4. **Initialize Database**
   ```bash
   python -m src.db.init
   ```

5. **Run Application**
   ```bash
   python app.py
   ```

**Done!** API is running at `http://localhost:5000`

---

## First API Calls

### 1. Health Check
```bash
curl http://localhost:5000/health
```

Response:
```json
{
  "status": "healthy",
  "checks": {
    "database": "connected",
    "redis": "connected",
    "external_api": "reachable"
  }
}
```

### 2. Get Character
```bash
curl http://localhost:5000/characters/1
```

Response:
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "name": "Rick Sanchez",
    "status": "Alive",
    "species": "Human",
    ...
  },
  "cache": {
    "hit": false,
    "ttl": 3600
  }
}
```

### 3. Search Characters
```bash
curl 'http://localhost:5000/characters/search?name=morty'
```

### 4. Check Cache Performance
```bash
curl http://localhost:5000/cache/stats
```

---

## View Logs

### Docker Compose
```bash
docker-compose logs -f api
```

### Local Python
```bash
# Logs appear in terminal where app.py runs
```

---

## Stop Services

### Docker Compose
```bash
docker-compose down
```

### Local Python
```bash
# Press Ctrl+C in terminal
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused | Check if services are running: `docker-compose ps` or `curl localhost:5000/health` |
| Database error | Verify database URL in `.env` and PostgreSQL is running |
| Redis error | Ensure Redis is running on port 6379 |
| Port 5000 in use | Kill existing process: `lsof -i :5000` and `kill <PID>` |

---

## Next Steps

- Read `docs/api/API_REFERENCE.md` for complete endpoint documentation
- Check `docs/guides/CACHE_HIT_MISS_DETECTION_GUIDE.md` to understand caching
- Review `docs/contributing/CODE_STANDARDS.md` before contributing
- See `docs/deployment/` for production deployment

## Need Help?

- Check `docs/contributing/` for development guides
- Review `docs/deployment/TROUBLESHOOTING_GUIDE.md` for common issues
- See `docs/examples/USAGE_EXAMPLES.md` for code samples
