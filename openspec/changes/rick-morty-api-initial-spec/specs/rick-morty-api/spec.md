## Purpose

Provides a queryable interface to retrieve Rick and Morty characters with support for filtering, pagination, and sorting to enable applications to access curated character data efficiently.

## ADDED Requirements

### Requirement: Query characters with filters
The system SHALL query the Rick and Morty public API and return only characters matching all of the following filter criteria:
- Species: Human
- Status: Alive  
- Origin: From Earth (any variant, e.g., Earth (C-137), Earth (Replacement Dimension))

#### Scenario: Query returns filtered characters
- **WHEN** a client requests characters via GET /characters
- **THEN** the response returns only human, alive characters from Earth

#### Scenario: Origin filter includes variants
- **WHEN** querying characters with origin filter
- **THEN** the system accepts and matches any "Earth" variant name (Earth, Earth (C-137), Earth (Replacement Dimension), etc.)

### Requirement: Pagination support
The system SHALL support offset-based pagination with the following parameters:
- `page`: Page number (default: 1, must be >= 1)
- `limit`: Number of results per page (default: 10, maximum: 50)

The response SHALL include pagination metadata:
- current_page: The requested page number
- limit: Items per page requested
- total_items: Total matching items across all pages
- total_pages: Number of pages available
- has_next: Boolean indicating if next page exists
- has_previous: Boolean indicating if previous page exists

#### Scenario: Pagination with defaults
- **WHEN** client requests /characters with no pagination parameters
- **THEN** response returns 10 items from page 1 with pagination metadata

#### Scenario: Pagination with custom limit
- **WHEN** client requests /characters?page=2&limit=5
- **THEN** response returns 5 items from page 2 and total_pages reflects the limit

#### Scenario: Limit exceeds maximum
- **WHEN** client requests with limit > 50
- **THEN** system caps the limit to 50 and returns maximum page size

### Requirement: Sorting capabilities
The system SHALL support sorting by the following fields:
- `name`: Sort by character name (alphabetically)
- `id`: Sort by character ID (numerically)

Sorting order options:
- `asc`: Ascending order (default)
- `desc`: Descending order

#### Scenario: Sort by name ascending
- **WHEN** client requests /characters?sort_by=name&sort_order=asc
- **THEN** results are ordered alphabetically by character name

#### Scenario: Sort by ID descending
- **WHEN** client requests /characters?sort_by=id&sort_order=desc
- **THEN** results are ordered by ID from highest to lowest

#### Scenario: Default sort order
- **WHEN** client requests /characters?sort_by=name (no sort_order)
- **THEN** results default to ascending order

### Requirement: HTTP Response format
The system SHALL return valid JSON responses with the following structure:
- `data`: Array of character objects (from Rick and Morty API with all fields)
- `pagination`: Object with pagination metadata (page, limit, total_items, total_pages, has_next, has_previous)
- `filters`: Object describing applied filters (species, status, origin)

#### Scenario: Successful response format
- **WHEN** GET /characters succeeds
- **THEN** response includes data array, pagination object, and filters object

### Requirement: Retrieve individual character by ID
The system SHALL allow retrieval of a specific character by ID, provided the character matches the filter criteria.

#### Scenario: Get character by matching ID
- **WHEN** client requests GET /characters/1
- **THEN** system returns the character object if it is human, alive, and from Earth

#### Scenario: Get character by non-matching ID
- **WHEN** client requests GET /characters/<id> where character does not match filters
- **THEN** system returns 400 error with message indicating character does not match filter criteria

#### Scenario: Non-existent character
- **WHEN** client requests GET /characters/<id> with invalid ID
- **THEN** system returns 404 error

## ADDED Requirements

### Requirement: Error handling for rate limits
The system SHALL handle rate limiting from the Rick and Morty API:
- When receiving a 429 (Too Many Requests) response from upstream API
- Return HTTP 429 to client with error message: "Rate limit exceeded. Please try again later."

#### Scenario: Rate limit from upstream API
- **WHEN** Rick and Morty API returns 429 status code
- **THEN** system returns 429 to client with appropriate error message

### Requirement: Error handling for service unavailability
The system SHALL handle service unavailability from the Rick and Morty API:
- When receiving a 503 (Service Unavailable) response from upstream API
- Return HTTP 503 to client with error message: "Service unavailable. Please try again later."
- When network timeout occurs (request timeout after 10 seconds)
- Return HTTP 503 to client with appropriate error message

#### Scenario: Upstream service unavailable
- **WHEN** Rick and Morty API returns 503 status code
- **THEN** system returns 503 to client with appropriate error message

#### Scenario: Request timeout
- **WHEN** upstream API does not respond within 10 seconds
- **THEN** system returns 503 error with "Service unavailable" message

### Requirement: Error handling for invalid requests
The system SHALL return HTTP 400 (Bad Request) for invalid request parameters:
- Invalid query parameter values (e.g., non-numeric page/limit)
- Character ID by filter mismatch (character exists but does not match filter criteria)

#### Scenario: Invalid page parameter
- **WHEN** client requests /characters?page=invalid
- **THEN** system returns 400 error with "Invalid request parameters" message

### Requirement: Health check endpoint
The system SHALL provide a health check endpoint:
- Endpoint: GET /health
- Response: JSON object with `{"status": "healthy"}` and HTTP 200

#### Scenario: Health check success
- **WHEN** client requests GET /health
- **THEN** system returns 200 with status "healthy"

### Requirement: API documentation endpoint
The system SHALL provide an API documentation endpoint:
- Endpoint: GET /
- Returns: JSON object containing message, version, list of endpoints, query parameters, and active filters

#### Scenario: Root endpoint documentation
- **WHEN** client requests GET /
- **THEN** system returns JSON with endpoint documentation and available query parameters
