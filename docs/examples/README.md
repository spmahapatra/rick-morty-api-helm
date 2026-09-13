# Examples and Tutorials

This directory contains practical examples, tutorials, and usage patterns for the Rick and Morty API.

## Contents

### Quick Start
📄 **[`QUICK_START.md`](QUICK_START.md)**
- 5-minute setup guide
- Docker Compose quick setup
- Local development setup
- First API calls
- Troubleshooting

### Usage Examples
📄 **[`USAGE_EXAMPLES.md`](USAGE_EXAMPLES.md)** *(Coming Soon)*
- Python code examples
- Bash/curl examples
- Common use cases
- Error handling patterns
- Performance tips

### Integration Examples
📄 **[`INTEGRATION_EXAMPLES.md`](INTEGRATION_EXAMPLES.md)** *(Coming Soon)*
- Third-party integrations
- Webhook setup (future)
- Real-world scenarios
- Advanced patterns

---

## Quick Links

| Need | Document |
|------|----------|
| Get started in 5 minutes | `QUICK_START.md` |
| See code examples | `USAGE_EXAMPLES.md` |
| Integrate with other systems | `INTEGRATION_EXAMPLES.md` |

---

## Most Common Tasks

### Get Started
```bash
git clone <repo>
cd setupAppCreDepHelmPkg
docker-compose up -d
curl http://localhost:5000/health
```

See `QUICK_START.md` for details.

### Call the API (Python)
```python
import requests

response = requests.get('http://localhost:5000/characters/1')
character = response.json()['data']
print(f"{character['name']} - {character['status']}")
```

See `USAGE_EXAMPLES.md` for more patterns.

### Call the API (cURL)
```bash
# Get character
curl http://localhost:5000/characters/1

# Search characters
curl 'http://localhost:5000/characters/search?name=rick'

# Check cache stats
curl http://localhost:5000/cache/stats
```

See `QUICK_START.md` for all endpoints.

### Monitor Performance
```python
import requests
import time

# First request (cache miss)
start = time.time()
response1 = requests.get('http://localhost:5000/characters/1')
time1 = (time.time() - start) * 1000

# Second request (cache hit)
start = time.time()
response2 = requests.get('http://localhost:5000/characters/1')
time2 = (time.time() - start) * 1000

print(f"Miss: {time1:.0f}ms, Hit: {time2:.0f}ms")
print(f"Cache hit data: {response2.json()['cache']}")
```

---

## Common Scenarios

### Scenario 1: Fetch Single Character
See `QUICK_START.md` → First API Calls → Get Character

### Scenario 2: Search Multiple Characters
See `QUICK_START.md` → First API Calls → Search Characters

### Scenario 3: Monitor Cache Performance
See `QUICK_START.md` → First API Calls → Check Cache Performance

### Scenario 4: Build a Web Application
See `USAGE_EXAMPLES.md` (when available)

### Scenario 5: Integrate with Another Service
See `INTEGRATION_EXAMPLES.md` (when available)

---

## Learning Path

1. **Beginner**: Start with `QUICK_START.md`
2. **Intermediate**: Read `USAGE_EXAMPLES.md` for patterns
3. **Advanced**: Study `INTEGRATION_EXAMPLES.md` for complex setups
4. **Expert**: Review `docs/architecture/` and `docs/deployment/` for deep dives

---

## Related Documentation

- **Architecture**: See [`docs/architecture/`](../architecture/) for system design
- **API Reference**: See [`docs/api/API_REFERENCE.md`](../api/API_REFERENCE.md) for endpoints
- **Deployment**: See [`docs/deployment/`](../deployment/) for production setup
- **Contributing**: See [`docs/contributing/DEVELOPMENT_SETUP.md`](../contributing/DEVELOPMENT_SETUP.md) for development

---

## In This Directory

```
examples/
├── README.md (this file)
├── QUICK_START.md
├── USAGE_EXAMPLES.md (coming soon)
└── INTEGRATION_EXAMPLES.md (coming soon)
```

## Status

| Document | Status |
|----------|--------|
| QUICK_START | ✅ Complete |
| USAGE_EXAMPLES | 🟡 Planned |
| INTEGRATION_EXAMPLES | 🟡 Planned |

---

## Need Help?

- **Getting started**: See `QUICK_START.md`
- **Specific issues**: See [`docs/deployment/TROUBLESHOOTING_GUIDE.md`](../deployment/TROUBLESHOOTING_GUIDE.md)
- **Code examples**: See `USAGE_EXAMPLES.md`
- **Architecture questions**: See [`docs/architecture/ARCHITECTURE_OVERVIEW.md`](../architecture/ARCHITECTURE_OVERVIEW.md)
