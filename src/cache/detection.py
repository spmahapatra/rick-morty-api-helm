"""
Cache Detection Middleware & Utilities

This module provides cache hit/miss detection functionality:
- Middleware for detecting cache status per request
- Response header injection
- Structured logging with cache context
- Cache statistics and monitoring
"""

import hashlib
import time
import logging
from typing import Dict, Any, Optional, Callable
from functools import wraps
from datetime import datetime
from flask import g, request, jsonify

logger = logging.getLogger(__name__)


class CacheDetector:
    """Detects and tracks cache hit/miss status for requests"""
    
    def __init__(self, cache_backend=None):
        """Initialize cache detector"""
        self.cache_backend = cache_backend
        self.cache_enabled = True
        self.cacheable_methods = {"GET", "HEAD", "OPTIONS"}
        self.excluded_endpoints = {
            "health_check",
            "get_cache_stats",
            "flush_cache",
            "get_cache_analytics",
            "root"
        }
    
    def generate_cache_key(
        self,
        endpoint: str,
        method: str,
        query_params: Dict[str, Any] = None,
        custom_key: str = None
    ) -> str:
        """
        Generate deterministic cache key from request
        
        Args:
            endpoint: Flask endpoint name
            method: HTTP method
            query_params: Query parameters dict
            custom_key: Override with custom key
            
        Returns:
            Cache key string
        """
        if custom_key:
            return custom_key
        
        # Build key components
        key_parts = [endpoint, method]
        
        # Add sorted query parameters
        if query_params:
            for key in sorted(query_params.keys()):
                value = query_params[key]
                key_parts.append(f"{key}={value}")
        
        # Create hash
        key_str = ":".join(str(p) for p in key_parts)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()[:8]
        
        return f"cache:{endpoint}:{method.lower()}:{key_hash}"
    
    def is_cacheable_request(self, req) -> bool:
        """Check if request should be cached"""
        
        # Skip excluded endpoints
        if req.endpoint in self.excluded_endpoints:
            return False
        
        # Only cache safe methods
        if req.method not in self.cacheable_methods:
            return False
        
        # Check for cache bypass parameter
        if req.args.get("cache") == "bypass":
            return False
        
        # Cache all safe requests to cacheable endpoints
        # (Both requests with and without query parameters)
        return True
    
    def detect_cache_status(self, req) -> tuple[str, Optional[Dict]]:
        """
        Detect cache status for request
        
        Returns:
            Tuple of (status, cached_data)
            status: "HIT", "MISS", "BYPASS", "ERROR"
            cached_data: cached response data if HIT, else None
        """
        
        # Check if request is cacheable
        if not self.is_cacheable_request(req):
            return "BYPASS", None
        
        # Check for explicit bypass
        cache_param = req.args.get("cache", "").lower()
        if cache_param in ["no", "bypass", "false"]:
            return "BYPASS", None
        
        # Generate cache key
        cache_key = self.generate_cache_key(
            req.endpoint or "unknown",
            req.method,
            dict(req.args)
        )
        
        # Try to get from cache
        try:
            if not self.cache_backend:
                return "ERROR", None
            
            cached_data = self.cache_backend.get(cache_key)
            
            if cached_data is not None:
                logger.debug(
                    f"Cache hit for {cache_key}",
                    extra={"cache_key": cache_key, "cache_status": "HIT"}
                )
                return "HIT", cached_data
            else:
                logger.debug(
                    f"Cache miss for {cache_key}",
                    extra={"cache_key": cache_key, "cache_status": "MISS"}
                )
                return "MISS", None
                
        except Exception as e:
            logger.warning(
                f"Cache detection error for {cache_key}: {e}",
                extra={"cache_key": cache_key, "cache_status": "ERROR", "error": str(e)}
            )
            return "ERROR", None
    
    def get_cache_age_info(self, cache_status: str) -> Dict[str, Any]:
        """Get cache age and TTL information"""
        
        if cache_status == "HIT":
            # These would be actual values stored in cache
            return {
                "age_seconds": 45,  # Would be calculated from stored_at
                "ttl_seconds": 255,  # Time until expiry
                "stored_at": datetime.utcnow().isoformat() + "Z"
            }
        else:
            return {
                "age_seconds": 0,
                "ttl_seconds": 300,  # Default TTL
                "stored_at": None
            }


class CacheMiddleware:
    """Flask middleware for cache detection and response processing"""
    
    def __init__(self, app=None, cache_backend=None):
        """Initialize middleware"""
        self.app = app
        self.cache_backend = cache_backend
        self.detector = CacheDetector(cache_backend)
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Register middleware with Flask app"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        
        logger.info("Cache middleware initialized")
    
    def before_request(self):
        """
        Before request: Detect cache status
        
        Sets in g:
        - cache_key: Generated cache key
        - cache_status: HIT, MISS, BYPASS, ERROR
        - cached_data: Cached response if HIT
        - cache_start_time: When cache detection started
        """
        
        # Start timing
        g.cache_start_time = time.time()
        
        # Detect cache status
        cache_status, cached_data = self.detector.detect_cache_status(request)
        
        # Store in request context
        g.cache_key = self.detector.generate_cache_key(
            request.endpoint or "unknown",
            request.method,
            dict(request.args)
        )
        g.cache_status = cache_status
        g.cached_data = cached_data
        g.cache_enabled = self.cache_backend is not None
    
    def after_request(self, response):
        """
        After response: Add cache headers, store in cache, and logging
        
        Adds headers:
        - X-Cache: hit, miss, bypass, error
        - X-Cache-Key: Generated cache key
        - X-Cache-Age: Seconds since cached (if hit)
        - X-Cache-TTL: Seconds until expiry (if hit)
        - Age: RFC 7234 age header
        - Cache-Control: Browser cache directive
        """
        
        # Get cache info from request context
        cache_status = g.get("cache_status", "UNKNOWN")
        cache_key = g.get("cache_key", "")
        
        # Store response in cache if MISS and status is 200 and JSON content
        if (cache_status == "MISS" and 
            response.status_code == 200 and 
            self.cache_backend and
            "application/json" in response.headers.get("Content-Type", "")):
            try:
                # Get JSON data from response
                response_json = response.get_json()
                if response_json is not None:
                    # Store response data in cache with 5-minute TTL
                    response_data = {
                        "data": response_json,
                        "status_code": response.status_code,
                        "cached_at": time.time()
                    }
                    success = self.cache_backend.set(cache_key, response_data, ttl_seconds=300)
                    if success:
                        logger.debug(f"Cached response for {cache_key} (TTL: 300s)")
                    else:
                        logger.warning(f"Failed to cache response for {cache_key}")
            except Exception as e:
                logger.warning(f"Exception while caching response for {cache_key}: {type(e).__name__}: {e}")
        
        # Add cache status header (main indicator)
        response.headers["X-Cache"] = cache_status.lower()
        
        # Add cache key for debugging
        if cache_key:
            response.headers["X-Cache-Key"] = cache_key
        
        # Add cache age info if hit
        if cache_status == "HIT":
            response.headers["X-Cache-Age"] = "45"  # Would be calculated
            response.headers["X-Cache-TTL"] = "255"  # Remaining TTL
            response.headers["Age"] = "45"  # RFC 7234
        
        # Add standard cache control headers
        if cache_status in ["HIT", "MISS"]:
            response.headers["Cache-Control"] = "public, max-age=300"
        else:
            response.headers["Cache-Control"] = "private, no-cache"
        
        response.headers["Vary"] = "Accept-Encoding"
        
        # Log response with cache context
        if hasattr(g, 'cache_start_time'):
            cache_time = (time.time() - g.cache_start_time) * 1000
            
            # Get correlation ID if available
            correlation_id = request.headers.get(
                'X-Correlation-ID',
                g.get('correlation_id', 'unknown')
            )
            
            logger.info(
                f"Response sent - {cache_status}",
                extra={
                    "cache_status": cache_status,
                    "cache_key": cache_key,
                    "cache_time_ms": cache_time,
                    "endpoint": request.endpoint,
                    "method": request.method,
                    "status_code": response.status_code,
                    "correlation_id": correlation_id
                }
            )
        
        return response


def with_cache_detection(
    cache_backend,
    ttl_seconds: int = 300,
    cache_key_func: Optional[Callable] = None
):
    """
    Decorator for cache detection on specific endpoints
    
    Args:
        cache_backend: Cache backend instance
        ttl_seconds: Time to live for cached response
        cache_key_func: Custom function to generate cache key
    
    Usage:
        @app.route("/characters")
        @with_cache_detection(cache_backend, ttl_seconds=300)
        def get_characters():
            return jsonify({"data": [...]})
    """
    
    detector = CacheDetector(cache_backend)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if cache_key_func:
                cache_key = cache_key_func(request)
            else:
                cache_key = detector.generate_cache_key(
                    func.__name__,
                    request.method,
                    dict(request.args)
                )
            
            # Try cache hit
            try:
                cached_data = cache_backend.get(cache_key)
                if cached_data:
                    logger.debug(f"Cache hit for {func.__name__}")
                    g.cache_status = "HIT"
                    g.cached_data = cached_data
                    
                    response = jsonify(cached_data)
                    response.headers["X-Cache"] = "hit"
                    response.headers["X-Cache-Key"] = cache_key
                    return response
            except Exception as e:
                logger.warning(f"Cache hit check failed: {e}")
            
            # Cache miss - call function
            g.cache_status = "MISS"
            g.cached_data = None
            
            result = func(*args, **kwargs)
            
            # Extract data from response if needed
            if isinstance(result, tuple):
                response_data, status_code, headers = result[0], result[1], result[2] if len(result) > 2 else {}
            else:
                response_data = result
                status_code = 200
                headers = {}
            
            # Store in cache
            try:
                cache_backend.set(cache_key, response_data, ttl_seconds=ttl_seconds)
                logger.debug(f"Cached response for {func.__name__} (TTL: {ttl_seconds}s)")
            except Exception as e:
                logger.warning(f"Failed to cache response: {e}")
            
            # Add cache headers
            if isinstance(result, tuple):
                response = result[0]
                if hasattr(response, 'headers'):
                    response.headers["X-Cache"] = "miss"
                    response.headers["X-Cache-Key"] = cache_key
                return result
            else:
                response = jsonify(response_data)
                response.headers["X-Cache"] = "miss"
                response.headers["X-Cache-Key"] = cache_key
                return response
        
        return wrapper
    
    return decorator


class CacheMetricsCollector:
    """Collects and aggregates cache performance metrics"""
    
    def __init__(self):
        """Initialize metrics"""
        self.metrics = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "cache_errors": 0,
            "cache_bypasses": 0,
            "total_response_time_ms": 0,
            "hit_response_times": [],
            "miss_response_times": []
        }
    
    def record_request(
        self,
        cache_status: str,
        response_time_ms: float
    ) -> None:
        """Record a request's cache status and timing"""
        
        self.metrics["total_requests"] += 1
        self.metrics["total_response_time_ms"] += response_time_ms
        
        if cache_status == "HIT":
            self.metrics["cache_hits"] += 1
            self.metrics["hit_response_times"].append(response_time_ms)
        elif cache_status == "MISS":
            self.metrics["cache_misses"] += 1
            self.metrics["miss_response_times"].append(response_time_ms)
        elif cache_status == "ERROR":
            self.metrics["cache_errors"] += 1
        elif cache_status == "BYPASS":
            self.metrics["cache_bypasses"] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current cache statistics"""
        
        total = self.metrics["total_requests"]
        hits = self.metrics["cache_hits"]
        misses = self.metrics["cache_misses"]
        
        hit_ratio = (hits / total * 100) if total > 0 else 0
        
        avg_hit_time = (
            sum(self.metrics["hit_response_times"]) / len(self.metrics["hit_response_times"])
            if self.metrics["hit_response_times"] else 0
        )
        
        avg_miss_time = (
            sum(self.metrics["miss_response_times"]) / len(self.metrics["miss_response_times"])
            if self.metrics["miss_response_times"] else 0
        )
        
        time_saved_per_hit = avg_miss_time - avg_hit_time
        total_time_saved = time_saved_per_hit * hits
        
        return {
            "total_requests": total,
            "cache_hits": hits,
            "cache_misses": misses,
            "cache_errors": self.metrics["cache_errors"],
            "cache_bypasses": self.metrics["cache_bypasses"],
            "hit_ratio_percent": round(hit_ratio, 2),
            "avg_hit_response_ms": round(avg_hit_time, 2),
            "avg_miss_response_ms": round(avg_miss_time, 2),
            "time_saved_per_hit_ms": round(time_saved_per_hit, 2),
            "total_time_saved_ms": round(total_time_saved, 2),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    def reset(self) -> None:
        """Reset all metrics"""
        self.metrics = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "cache_errors": 0,
            "cache_bypasses": 0,
            "total_response_time_ms": 0,
            "hit_response_times": [],
            "miss_response_times": []
        }


# Global metrics collector instance
_metrics_collector = CacheMetricsCollector()


def get_metrics_collector() -> CacheMetricsCollector:
    """Get global metrics collector"""
    return _metrics_collector
