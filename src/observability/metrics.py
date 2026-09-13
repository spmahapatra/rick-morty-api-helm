"""Metrics collection"""

import logging
import time
from typing import Dict, Any
from prometheus_client import Counter, Histogram, Gauge

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Prometheus metrics collection"""
    
    def __init__(self, app_name: str = "rick_morty_api"):
        """Initialize metrics collector"""
        self.app_name = app_name
        
        # Request metrics
        self.request_count = Counter(
            f"{app_name}_requests_total",
            "Total requests",
            ["method", "endpoint", "status"]
        )
        
        self.request_latency = Histogram(
            f"{app_name}_request_duration_seconds",
            "Request latency in seconds",
            ["method", "endpoint"],
            buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0)
        )
        
        # Cache metrics
        self.cache_hits = Counter(
            f"{app_name}_cache_hits_total",
            "Cache hits",
            ["cache_backend"]
        )
        
        self.cache_misses = Counter(
            f"{app_name}_cache_misses_total",
            "Cache misses",
            ["cache_backend"]
        )
        
        self.cache_errors = Counter(
            f"{app_name}_cache_errors_total",
            "Cache errors",
            ["cache_backend"]
        )
        
        # Database metrics
        self.db_query_latency = Histogram(
            f"{app_name}_db_query_duration_seconds",
            "Database query latency",
            ["operation"]
        )
        
        self.db_connection_pool_size = Gauge(
            f"{app_name}_db_pool_size",
            "Database connection pool size"
        )
        
        # Circuit breaker metrics
        self.circuit_breaker_state = Gauge(
            f"{app_name}_circuit_breaker_state",
            "Circuit breaker state (0=CLOSED, 1=OPEN, 2=HALF_OPEN)",
            ["circuit"]
        )
        
        # Rate limiting metrics
        self.rate_limit_exceeded = Counter(
            f"{app_name}_rate_limit_exceeded_total",
            "Rate limit violations",
            ["consumer"]
        )
        
        # Error metrics
        self.errors_total = Counter(
            f"{app_name}_errors_total",
            "Total errors",
            ["error_type", "endpoint"]
        )
    
    def record_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        latency_seconds: float
    ) -> None:
        """Record request metrics"""
        self.request_count.labels(
            method=method,
            endpoint=endpoint,
            status=status_code
        ).inc()
        
        self.request_latency.labels(
            method=method,
            endpoint=endpoint
        ).observe(latency_seconds)
    
    def record_cache_hit(self, backend: str = "redis") -> None:
        """Record cache hit"""
        self.cache_hits.labels(cache_backend=backend).inc()
    
    def record_cache_miss(self, backend: str = "redis") -> None:
        """Record cache miss"""
        self.cache_misses.labels(cache_backend=backend).inc()
    
    def record_cache_error(self, backend: str = "redis") -> None:
        """Record cache error"""
        self.cache_errors.labels(cache_backend=backend).inc()
    
    def record_db_query(self, operation: str, latency_seconds: float) -> None:
        """Record database query latency"""
        self.db_query_latency.labels(operation=operation).observe(latency_seconds)
    
    def set_db_pool_size(self, size: int) -> None:
        """Set database pool size gauge"""
        self.db_connection_pool_size.set(size)
    
    def record_circuit_breaker_state(self, circuit: str, state_value: int) -> None:
        """Record circuit breaker state (0=CLOSED, 1=OPEN, 2=HALF_OPEN)"""
        self.circuit_breaker_state.labels(circuit=circuit).set(state_value)
    
    def record_rate_limit_exceeded(self, consumer: str) -> None:
        """Record rate limit violation"""
        self.rate_limit_exceeded.labels(consumer=consumer).inc()
    
    def record_error(self, error_type: str, endpoint: str) -> None:
        """Record error"""
        self.errors_total.labels(error_type=error_type, endpoint=endpoint).inc()
    
    def get_metrics(self) -> str:
        """Get metrics in Prometheus text format"""
        from prometheus_client import REGISTRY, generate_latest, CollectorRegistry
        return generate_latest(REGISTRY).decode('utf-8')
