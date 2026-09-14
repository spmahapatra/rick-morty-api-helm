## 1. Core API Implementation

- [x] 1.1 Implement RickAndMortyClient class for upstream API communication (fetch_characters method, error handling) and verify unit tests for client initialization and fetch methods pass
- [x] 1.2 Implement character filtering logic (filter_characters_by_origin) to match only Earth variants and verify the origin filter test passes with test data
- [x] 1.3 Implement sorting logic (sort_characters) supporting name and ID fields with asc/desc order and verify sort test cases pass
- [x] 1.4 Implement pagination logic (paginate_characters) with offset-based approach and verify pagination metadata is accurate in test scenarios

## 2. REST API Endpoints

- [x] 2.1 Implement GET / endpoint returning API documentation with endpoint list, query parameters, and active filters and verify root endpoint test passes
- [x] 2.2 Implement GET /health endpoint returning {"status": "healthy"} with 200 status and verify health check test passes
- [x] 2.3 Implement GET /characters endpoint with query parameter support (page, limit, sort_by, sort_order), parameter validation, and response structure and verify characters endpoint test passes with default and custom parameters
- [x] 2.4 Implement GET /characters/<id> endpoint to retrieve individual character by ID, verify filter criteria match, and return appropriate error codes and verify character by ID test passes

## 3. Error Handling

- [x] 3.1 Implement HTTP status code mapping for upstream API errors (400, 404, 429, 503) with appropriate error messages and verify status code test cases pass
- [x] 3.2 Implement request timeout handling (10-second timeout) returning 503 with service unavailable message and verify timeout behavior in tests
- [x] 3.3 Implement input validation for query parameters (page, limit, sort_by, sort_order) with appropriate error responses and verify invalid parameter test cases pass
- [x] 3.4 Implement custom exception class RickAndMortyAPIError with status code and message tracking and verify error handling decorator catches and formats exceptions correctly

## 4. Testing and Validation

- [x] 4.1 Verify all unit tests pass with test coverage for filtering, pagination, sorting, and error scenarios by running `python -m unittest test_app.py -v`
- [x] 4.2 Verify health check endpoint responds correctly with `curl http://localhost:5000/health`
- [x] 4.3 Verify root endpoint documentation is accessible with `curl http://localhost:5000/`
- [x] 4.4 Test manual character queries with various parameters (e.g., `curl 'http://localhost:5000/characters?page=1&limit=5&sort_by=name'`) and verify response structure matches spec
- [x] 4.5 Verify error handling by testing invalid parameters and observing appropriate HTTP status codes (400, 404, 429, 503)

## 5. Configuration and Deployment

- [x] 5.1 Verify config.py provides environment-specific settings (development, testing, production) and can be imported without errors
- [x] 5.2 Verify requirements.txt includes all dependencies (Flask, requests, gunicorn, Flask-CORS) and `pip install -r requirements.txt` succeeds
- [x] 5.3 Verify Dockerfile builds successfully with `docker build -t rick-morty-api .` and container runs with `docker run -p 5000:5000 rick-morty-api`
- [x] 5.4 Verify docker-compose.yml is valid YAML and `docker-compose up -d` starts the service without errors
- [x] 5.5 Verify start.sh script runs without errors and sets up virtual environment and dependencies correctly

## 6. Documentation

- [x] 6.1 Verify README.md is complete with installation, running, endpoint documentation, error handling, and example curl commands
- [x] 6.2 Verify .env.example file contains all configuration options with sensible defaults
- [x] 6.3 Verify code includes docstrings for all classes, methods, and functions describing purpose, parameters, and return values
- [x] 6.4 Verify API documentation endpoint (GET /) includes all required information as specified

## 7. Integration Testing

- [x] 7.1 Run full test suite and verify all tests pass: `python -m unittest test_app.py -v`
- [x] 7.2 Start application in development mode (`python app.py`) and verify it responds to requests without errors
- [x] 7.3 Test pagination across multiple pages and verify total_pages, has_next, has_previous are accurate
- [x] 7.4 Test sorting in both ascending and descending order and verify results are correctly ordered
- [x] 7.5 Test character retrieval by ID for both matching and non-matching filter criteria