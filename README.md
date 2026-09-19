# Rick and Morty Character API

![Project Banner](docs/assets/banner.jpg)

![Build Status](https://img.shields.io/github/actions/workflow/status/spmahapatra/rick-morty-api-helm/ci.yml?branch=main&style=for-the-badge)
![Version](https://img.shields.io/github/v/release/spmahapatra/rick-morty-api-helm?include_prereleases&sort=semver&style=for-the-badge)
![Docker Size](https://img.shields.io/docker/image-size/spmahapatra/rick-morty-api/latest?style=for-the-badge)
![License](https://img.shields.io/github/license/spmahapatra/rick-morty-api-helm?style=for-the-badge)

A RESTful API application built with Python and Flask that queries the Rick and Morty API to retrieve filtered character data.


## Features

- **Filtered Character Data**: Automatically filters for:
  - Species: Human
  - Status: Alive
  - Origin: Earth (any variant, e.g., Earth (C-137), Earth (Replacement Dimension))

- **RESTful API**: Exposes endpoints returning filtered character data in JSON format

- **Pagination Support**: Query parameters for `page` and `limit` to control result set size

- **Sorting Capabilities**: Sort by `name` or `id` in ascending or descending order

- **Error Handling**: Comprehensive error handling for:
  - 400: Invalid request parameters
  - 404: Character/endpoint not found
  - 429: Rate limit exceeded
  - 503: Service unavailable

- **Health Check**: Built-in health check endpoint for monitoring

## Requirements

- Python 3.8+
- Flask 3.0.0
- requests 2.31.0
- Other dependencies in `requirements.txt`

## Installation

1. Clone or download this repository

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

### Development Mode
```bash
python app.py
```

The API will be available at `http://localhost:5000`

### Production Mode (with Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## API Endpoints

### 1. Health Check
```
GET /health
```
Returns the health status of the application.

**Response:**
```json
{
  "status": "healthy"
}
```

### 2. Root Endpoint
```
GET /
```
Returns API documentation and available endpoints.

**Response:**
```json
{
  "message": "Rick and Morty Character API",
  "version": "1.0.0",
  "endpoints": {...},
  "query_parameters": {...},
  "filters": {...}
}
```

### 3. Get Filtered Characters
```
GET /characters
```

Returns paginated, sorted, and filtered character data.

**Query Parameters:**
- `page` (integer, default: 1): Page number for pagination
- `limit` (integer, default: 10, max: 50): Number of items per page
- `sort_by` (string, default: "name"): Sort by "name" or "id"
- `sort_order` (string, default: "asc"): Sort order "asc" or "desc"

**Examples:**

Get first page with 10 characters:
```bash
curl http://localhost:5000/characters
```

Get second page with 5 characters per page:
```bash
curl "http://localhost:5000/characters?page=2&limit=5"
```

Sort by name in descending order:
```bash
curl "http://localhost:5000/characters?sort_by=name&sort_order=desc"
```

Sort by ID in ascending order with custom limit:
```bash
curl "http://localhost:5000/characters?sort_by=id&limit=20"
```

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "name": "Rick Sanchez",
      "status": "Alive",
      "species": "Human",
      "type": "",
      "gender": "Male",
      "origin": {
        "name": "Earth (C-137)",
        "url": "..."
      },
      "location": {...},
      "image": "...",
      "episode": [...],
      "url": "...",
      "created": "..."
    }
    // ... more characters
  ],
  "pagination": {
    "current_page": 1,
    "limit": 10,
    "total_items": 47,
    "total_pages": 5,
    "has_next": true,
    "has_previous": false
  },
  "filters": {
    "species": "human",
    "status": "alive",
    "origin": "Earth (any variant)"
  }
}
```

### 4. Get Character by ID
```
GET /characters/<id>
```

Returns details for a specific character by ID (if it matches the filters).

**Example:**
```bash
curl http://localhost:5000/characters/1
```

**Response:**
```json
{
  "data": {
    "id": 1,
    "name": "Rick Sanchez",
    "status": "Alive",
    "species": "Human",
    ...
  }
}
```

## Error Handling

### 400 Bad Request
Invalid request parameters or character doesn't match filters.
```json
{
  "error": "Invalid request parameters"
}
```

### 404 Not Found
Character or endpoint not found.
```json
{
  "error": "Character not found"
}
```

### 429 Rate Limit Exceeded
Rick and Morty API rate limit reached.
```json
{
  "error": "Rate limit exceeded. Please try again later."
}
```

### 503 Service Unavailable
Rick and Morty API is down or unreachable.
```json
{
  "error": "Service unavailable. Please try again later."
}
```

### 500 Internal Server Error
Unexpected server error.
```json
{
  "error": "Internal server error"
}
```

## Testing

Run the test suite:
```bash
python -m pytest test_app.py -v
```

Or use unittest:
```bash
python -m unittest test_app.py -v
```

## Architecture

### Components

1. **RickAndMortyClient**: Handles communication with the Rick and Morty API
   - Manages HTTP requests
   - Error handling and status code mapping
   - Request timeouts and retries

2. **Filtering Logic**: 
   - `filter_characters_by_origin()`: Filters by Earth variants
   - Applied after fetching from Rick and Morty API

3. **Sorting Logic**:
   - `sort_characters()`: Sorts by name or ID
   - Supports ascending and descending order

4. **Pagination Logic**:
   - `paginate_characters()`: Implements offset-based pagination
   - Returns pagination metadata

5. **Error Handling**:
   - Custom exception: `RickAndMortyAPIError`
   - Decorator: `handle_api_errors` for consistent error responses
   - HTTP status code handlers for 400, 404, 429, 503

## Configuration

Key constants in `app.py`:
- `RICK_AND_MORTY_API_BASE_URL`: Base URL for Rick and Morty API
- `DEFAULT_PAGE`: Default pagination page (1)
- `DEFAULT_LIMIT`: Default items per page (10)
- `MAX_LIMIT`: Maximum items per page (50)
- `FILTERS`: Applied filter criteria (species, status, origin variants)

## Deployment

### Docker

Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:
```bash
docker build -t rick-morty-api .
docker run -p 5000:5000 rick-morty-api
```

### Environment Variables

Create a `.env` file for environment-specific settings (optional):
```
FLASK_ENV=production
FLASK_DEBUG=False
RICK_AND_MORTY_API_BASE_URL=https://rickandmortyapi.com/api
```

## Performance Considerations

- The application fetches from page 1 of Rick and Morty API and applies filters client-side
- For production, consider caching results or using a database
- Rate limiting is handled gracefully with appropriate error messages
- Connection timeouts set to 10 seconds to prevent hanging requests

## Future Improvements

- Implement caching (Redis/Memcached)
- Add database persistence
- Rate limiting implementation
- GraphQL support
- WebSocket for real-time updates
- API key authentication
- Request logging and analytics

## License

MIT License

## Support

For issues or questions, refer to the Rick and Morty API documentation:
https://rickandmortyapi.com/documentation
