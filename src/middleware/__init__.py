"""Middleware for request processing"""

from functools import wraps
from flask import request, g
import uuid
import logging

logger = logging.getLogger(__name__)


def correlation_id_middleware(f):
    """Middleware to inject correlation ID"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get or generate correlation ID
        correlation_id = request.headers.get("X-Correlation-ID")
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
        
        # Store in context
        g.correlation_id = correlation_id
        
        # Call the function
        response = f(*args, **kwargs)
        
        # Add correlation ID to response headers
        if hasattr(response, "headers"):
            response.headers["X-Correlation-ID"] = correlation_id
        
        return response
    
    return decorated_function


def rate_limit_middleware(rate_limiter):
    """Middleware factory for rate limiting"""
    def middleware(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get consumer ID (IP address or API key)
            consumer_id = request.remote_addr
            
            # Check rate limit
            result = rate_limiter.check_rate_limit(consumer_id)
            
            if not result['allowed']:
                from flask import jsonify
                response = jsonify({
                    "error": "Rate limit exceeded",
                    "remaining": result['remaining'],
                    "reset_time": result['reset_time']
                })
                response.status_code = 429
                response.headers['Retry-After'] = str(result['retry_after_s'])
                return response
            
            # Store rate limit info in context
            g.rate_limit_info = result
            
            # Call the function
            return f(*args, **kwargs)
        
        return decorated_function
    
    return middleware


def request_logging_middleware(metrics_collector):
    """Middleware factory for request logging"""
    def middleware(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            import time
            
            start_time = time.time()
            
            try:
                response = f(*args, **kwargs)
                latency_seconds = time.time() - start_time
                
                # Record metrics
                status_code = response.status_code if hasattr(response, "status_code") else 200
                metrics_collector.record_request(
                    method=request.method,
                    endpoint=request.path,
                    status_code=status_code,
                    latency_seconds=latency_seconds
                )
                
                return response
            except Exception as e:
                latency_seconds = time.time() - start_time
                metrics_collector.record_error(
                    error_type=type(e).__name__,
                    endpoint=request.path
                )
                raise
        
        return decorated_function
    
    return middleware
