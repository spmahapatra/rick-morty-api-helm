"""
Rick and Morty Character API - RESTful Application
Queries the Rick and Morty API to retrieve filtered character data
"""

from flask import Flask, request, jsonify, g
from flask_cors import CORS
from functools import wraps
import requests
from typing import Dict, List, Any, Tuple
import logging
import uuid
import time

# Configure structured JSON logging
from src.observability.logging import setup_logging, StructuredLogger, set_correlation_id, get_correlation_id

setup_logging(level="INFO", format_type="json")
logger = StructuredLogger(__name__)

# Import cache detection
from src.cache.detection import CacheMiddleware, get_metrics_collector
from config import get_cache_backend

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize cache middleware
cache_backend = get_cache_backend()
cache_middleware = CacheMiddleware(app, cache_backend)
metrics_collector = get_metrics_collector()

# Constants
RICK_AND_MORTY_API_BASE_URL = "https://rickandmortyapi.com/api"
DEFAULT_PAGE = 1
DEFAULT_LIMIT = 10
MAX_LIMIT = 50

# Species, Status, and Origin filters
FILTERS = {
    "species": "human",
    "status": "alive",
    "origin_variants": [
        "earth (c-137)",
        "earth (replacement dimension)",
        "earth",
    ]
}


class RickAndMortyAPIError(Exception):
    """Custom exception for Rick and Morty API errors"""
    pass


def handle_api_errors(f):
    """Decorator to handle API errors gracefully"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        correlation_id = request.headers.get('X-Correlation-ID', str(uuid.uuid4()))
        set_correlation_id(correlation_id)
        
        try:
            return f(*args, **kwargs)
        except RickAndMortyAPIError as e:
            logger.error(
                "Rick and Morty API error occurred",
                error_type="RickAndMortyAPIError",
                error_message=str(e),
                status_code=e.status_code,
                correlation_id=correlation_id,
                endpoint=request.endpoint,
                method=request.method
            )
            return jsonify({"error": str(e)}), e.status_code
        except Exception as e:
            logger.error(
                "Unexpected error occurred",
                error_type=type(e).__name__,
                error_message=str(e),
                correlation_id=correlation_id,
                endpoint=request.endpoint,
                method=request.method
            )
            return jsonify({"error": "Internal server error"}), 500
    return decorated_function


class RickAndMortyClient:
    """Client for interacting with Rick and Morty API"""
    
    def __init__(self, base_url: str = RICK_AND_MORTY_API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        
    def fetch_characters(self, page: int = 1, status: str = None, species: str = None) -> Dict[str, Any]:
        """
        Fetch characters from the Rick and Morty API
        
        Args:
            page: Page number (1-indexed)
            status: Filter by status (e.g., 'alive', 'dead')
            species: Filter by species (e.g., 'human')
            
        Returns:
            Dictionary containing the API response
            
        Raises:
            RickAndMortyAPIError: If API request fails
        """
        try:
            url = f"{self.base_url}/character"
            params = {"page": page}
            
            if status:
                params["status"] = status
            if species:
                params["species"] = species
                
            response = self.session.get(url, params=params, timeout=10)
            
            # Handle different HTTP status codes
            if response.status_code == 400:
                raise RickAndMortyAPIError("Invalid request parameters", 400)
            elif response.status_code == 429:
                raise RickAndMortyAPIError("Rate limit exceeded. Please try again later.", 429)
            elif response.status_code == 503:
                raise RickAndMortyAPIError("Service unavailable. Please try again later.", 503)
            elif response.status_code == 404:
                raise RickAndMortyAPIError("Character not found", 404)
            elif response.status_code != 200:
                raise RickAndMortyAPIError(f"API returned status code {response.status_code}", response.status_code)
                
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(
                "Failed to fetch data from Rick and Morty API",
                error_type=type(e).__name__,
                error_message=str(e),
                url=url,
                params=params,
                timeout=10
            )
            raise RickAndMortyAPIError(f"Failed to fetch data from Rick and Morty API: {str(e)}", 503)


def filter_characters_by_origin(characters: List[Dict]) -> List[Dict]:
    """
    Filter characters by origin variants (Earth variants)
    
    Args:
        characters: List of character dictionaries
        
    Returns:
        Filtered list of characters from Earth
    """
    filtered = []
    for char in characters:
        origin_name = char.get("origin", {}).get("name", "").lower()
        for variant in FILTERS["origin_variants"]:
            if variant in origin_name:
                filtered.append(char)
                break
    return filtered


def sort_characters(characters: List[Dict], sort_by: str = "name", reverse: bool = False) -> List[Dict]:
    """
    Sort characters by specified field
    
    Args:
        characters: List of character dictionaries
        sort_by: Field to sort by ('name' or 'id')
        reverse: Whether to sort in descending order
        
    Returns:
        Sorted list of characters
    """
    if sort_by == "id":
        return sorted(characters, key=lambda x: x.get("id", 0), reverse=reverse)
    else:  # Default to 'name'
        return sorted(characters, key=lambda x: x.get("name", ""), reverse=reverse)


def paginate_characters(characters: List[Dict], page: int, limit: int) -> Tuple[List[Dict], Dict]:
    """
    Paginate characters list
    
    Args:
        characters: List of character dictionaries
        page: Page number (1-indexed)
        limit: Number of items per page
        
    Returns:
        Tuple of (paginated_characters, pagination_info)
    """
    total = len(characters)
    max_page = (total + limit - 1) // limit  # Ceiling division
    
    if page < 1 or page > max_page:
        page = 1
        
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    
    paginated = characters[start_idx:end_idx]
    
    pagination_info = {
        "current_page": page,
        "limit": limit,
        "total_items": total,
        "total_pages": max_page,
        "has_next": page < max_page,
        "has_previous": page > 1
    }
    
    return paginated, pagination_info


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint with structured logging"""
    logger.info(
        "Health check performed",
        status="healthy",
        correlation_id=get_correlation_id()
    )
    return jsonify({"status": "healthy"}), 200


@app.route("/api/cache/stats", methods=["GET"])
def get_cache_stats():
    """Get cache statistics from backend"""
    try:
        if not cache_backend:
            return jsonify({"error": "Cache not configured"}), 503
        
        stats = cache_backend.get_stats()
        
        logger.info(
            "Cache stats retrieved",
            cache_stats=stats,
            correlation_id=get_correlation_id()
        )
        
        return jsonify({
            "status": "ok",
            "cache_backend": stats,
            "metrics": metrics_collector.get_stats(),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }), 200
        
    except Exception as e:
        logger.error(
            "Failed to get cache stats",
            error=str(e),
            correlation_id=get_correlation_id()
        )
        return jsonify({"error": "Failed to get cache stats"}), 500


@app.route("/api/cache/flush", methods=["POST"])
def flush_cache():
    """Flush cache (admin endpoint)"""
    try:
        if not cache_backend:
            return jsonify({"error": "Cache not configured"}), 503
        
        if cache_backend.flush():
            metrics_collector.reset()
            logger.info(
                "Cache flushed",
                correlation_id=get_correlation_id()
            )
            return jsonify({"status": "ok", "message": "Cache flushed"}), 200
        else:
            return jsonify({"error": "Failed to flush cache"}), 500
            
    except Exception as e:
        logger.error(
            "Cache flush failed",
            error=str(e),
            correlation_id=get_correlation_id()
        )
        return jsonify({"error": "Cache flush failed"}), 500


@app.route("/api/cache/analytics", methods=["GET"])
def get_cache_analytics():
    """Get detailed cache analytics for monitoring"""
    try:
        backend_stats = cache_backend.get_stats() if cache_backend else {}
        metrics = metrics_collector.get_stats()
        
        return jsonify({
            "status": "ok",
            "backend_stats": backend_stats,
            "request_metrics": metrics,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }), 200
        
    except Exception as e:
        logger.error(
            "Failed to get cache analytics",
            error=str(e),
            correlation_id=get_correlation_id()
        )
        return jsonify({"error": "Failed to get analytics"}), 500


@app.route("/characters", methods=["GET"])
@app.route("/characters/", methods=["GET"])
@handle_api_errors
def get_characters():
    """
    Retrieve filtered characters from Rick and Morty API
    
    Query Parameters:
        - page: Page number (default: 1)
        - limit: Items per page (default: 10, max: 50)
        - sort_by: Sort field - 'name' or 'id' (default: 'name')
        - sort_order: 'asc' or 'desc' (default: 'asc')
        
    Returns:
        JSON response with filtered, sorted, and paginated character data
    """
    try:
        # Get query parameters
        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", DEFAULT_LIMIT, type=int)
        sort_by = request.args.get("sort_by", "name", type=str).lower()
        sort_order = request.args.get("sort_order", "asc", type=str).lower()
        
        # Validate parameters
        if page < 1:
            page = 1
        if limit < 1:
            limit = DEFAULT_LIMIT
        if limit > MAX_LIMIT:
            limit = MAX_LIMIT
        if sort_by not in ["name", "id"]:
            sort_by = "name"
        if sort_order not in ["asc", "desc"]:
            sort_order = "asc"
            
        reverse = sort_order == "desc"
        
        # Fetch characters from Rick and Morty API
        client = RickAndMortyClient()
        api_response = client.fetch_characters(
            page=1,  # Fetch from first page initially
            status=FILTERS["status"],
            species=FILTERS["species"]
        )
        
        # Extract characters
        characters = api_response.get("results", [])
        
        # Filter by origin (Earth variants)
        characters = filter_characters_by_origin(characters)
        
        # Sort characters
        characters = sort_characters(characters, sort_by=sort_by, reverse=reverse)
        
        # Paginate characters
        paginated_characters, pagination_info = paginate_characters(characters, page, limit)
        
        return jsonify({
            "data": paginated_characters,
            "pagination": pagination_info,
            "filters": {
                "species": FILTERS["species"],
                "status": FILTERS["status"],
                "origin": "Earth (any variant)"
            }
        }), 200
        
    except RickAndMortyAPIError as e:
        logger.error(
            "API error in get_filtered_characters",
            error_message=str(e),
            filters={"species": FILTERS["species"], "status": FILTERS["status"]},
            page=1
        )
        raise


@app.route("/characters/<int:character_id>", methods=["GET"])
@handle_api_errors
def get_character_by_id(character_id: int):
    """
    Retrieve a specific character by ID
    
    Args:
        character_id: Character ID
        
    Returns:
        JSON response with character data or error
    """
    try:
        client = RickAndMortyClient()
        url = f"{RICK_AND_MORTY_API_BASE_URL}/character/{character_id}"
        
        response = client.session.get(url, timeout=10)
        
        if response.status_code == 404:
            raise RickAndMortyAPIError("Character not found", 404)
        elif response.status_code == 429:
            raise RickAndMortyAPIError("Rate limit exceeded", 429)
        elif response.status_code == 503:
            raise RickAndMortyAPIError("Service unavailable", 503)
        elif response.status_code != 200:
            raise RickAndMortyAPIError(f"API error: {response.status_code}", response.status_code)
            
        character = response.json()
        
        # Verify it matches our filters
        if (character.get("species", "").lower() != FILTERS["species"] or
            character.get("status", "").lower() != FILTERS["status"]):
            raise RickAndMortyAPIError("Character does not match filter criteria", 400)
            
        origin_name = character.get("origin", {}).get("name", "").lower()
        origin_match = any(variant in origin_name for variant in FILTERS["origin_variants"])
        if not origin_match:
            raise RickAndMortyAPIError("Character origin does not match filter criteria", 400)
            
        return jsonify({"data": character}), 200
        
    except RickAndMortyAPIError as e:
        raise


@app.route("/", methods=["GET"])
def root():
    """Root endpoint with API documentation"""
    return jsonify({
        "message": "Rick and Morty Character API",
        "version": "1.0.0",
        "endpoints": {
            "GET /health": "Health check",
            "GET /characters": "List filtered characters (supports pagination and sorting)",
            "GET /characters/<id>": "Get specific character by ID"
        },
        "query_parameters": {
            "page": "Page number (default: 1)",
            "limit": "Items per page (default: 10, max: 50)",
            "sort_by": "Sort by 'name' or 'id' (default: 'name')",
            "sort_order": "Sort order 'asc' or 'desc' (default: 'asc')"
        },
        "filters": {
            "species": "Human",
            "status": "Alive",
            "origin": "Earth (any variant)"
        }
    }), 200


@app.before_request
def log_request():
    """Log incoming request with structured logging"""
    correlation_id = request.headers.get('X-Correlation-ID', str(uuid.uuid4()))
    set_correlation_id(correlation_id)
    request.start_time = time.time()
    
    logger.info(
        "Incoming request",
        method=request.method,
        path=request.path,
        query_string=request.query_string.decode('utf-8') if request.query_string else None,
        remote_addr=request.remote_addr,
        correlation_id=correlation_id
    )


@app.after_request
def log_response(response):
    """Log response with structured logging and cache status"""
    if hasattr(request, 'start_time'):
        elapsed_time = time.time() - request.start_time
    else:
        elapsed_time = 0
    
    # Get cache status from middleware
    cache_status = g.get("cache_status", "UNKNOWN")
    cache_key = g.get("cache_key", "")
    
    # Record metrics if cache status available
    if cache_status in ["HIT", "MISS", "ERROR", "BYPASS"]:
        metrics_collector.record_request(cache_status, elapsed_time * 1000)
    
    # Log response with cache context
    logger.info(
        "Response sent",
        method=request.method,
        path=request.path,
        status_code=response.status_code,
        elapsed_time_ms=round(elapsed_time * 1000, 2),
        cache_status=cache_status,
        cache_key=cache_key,
        correlation_id=get_correlation_id()
    )
    
    return response


@app.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors"""
    logger.warning(
        "Bad request error",
        error_type="BadRequest",
        path=request.path,
        correlation_id=get_correlation_id()
    )
    return jsonify({"error": "Bad request"}), 400


@app.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors"""
    logger.warning(
        "Not found error",
        error_type="NotFound",
        path=request.path,
        correlation_id=get_correlation_id()
    )
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(429)
def rate_limit_exceeded(error):
    """Handle 429 Rate Limit errors"""
    logger.warning(
        "Rate limit exceeded",
        error_type="RateLimitExceeded",
        path=request.path,
        correlation_id=get_correlation_id()
    )
    return jsonify({"error": "Rate limit exceeded"}), 429


@app.errorhandler(503)
def service_unavailable(error):
    """Handle 503 Service Unavailable errors"""
    logger.error(
        "Service unavailable error",
        error_type="ServiceUnavailable",
        path=request.path,
        correlation_id=get_correlation_id()
    )
    return jsonify({"error": "Service unavailable"}), 503


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
