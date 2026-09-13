"""Health check implementation"""

import logging
import time
from typing import Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)


class HealthChecker:
    """Deep health check for dependencies"""
    
    def __init__(self):
        """Initialize health checker"""
        self.checks: Dict[str, Callable] = {}
    
    def register_check(self, name: str, check_func: Callable) -> None:
        """Register a health check function"""
        self.checks[name] = check_func
    
    def perform_check(self, name: str) -> Dict[str, Any]:
        """Perform a specific health check"""
        if name not in self.checks:
            return {
                "status": "unknown",
                "error": f"No check registered for '{name}'"
            }
        
        try:
            check_func = self.checks[name]
            start_time = time.time()
            result = check_func()
            latency_ms = (time.time() - start_time) * 1000
            
            return {
                "status": result.get("status", "unknown"),
                "latency_ms": round(latency_ms, 2),
                "details": result.get("details", {})
            }
        except Exception as e:
            logger.error(f"Health check '{name}' failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def perform_all_checks(self) -> Dict[str, Any]:
        """Perform all registered health checks"""
        checks_result = {}
        critical_failures = []
        
        for name in self.checks:
            result = self.perform_check(name)
            checks_result[name] = result
            
            # Track critical failures
            if result.get("status") != "healthy" and name in ["database", "cache"]:
                critical_failures.append(name)
        
        # Determine overall status
        overall_status = "unhealthy" if critical_failures else "healthy"
        
        return {
            "status": overall_status,
            "timestamp": time.time(),
            "checks": checks_result,
            "critical_failures": critical_failures
        }


def create_database_check(db_connection) -> Callable:
    """Create database health check function"""
    def check():
        try:
            # Simple connectivity check
            with db_connection.engine.connect() as conn:
                conn.execute("SELECT 1")
            return {"status": "healthy", "details": {"connected": True}}
        except Exception as e:
            return {
                "status": "unhealthy",
                "details": {"error": str(e)}
            }
    return check


def create_cache_check(cache_backend) -> Callable:
    """Create cache health check function"""
    def check():
        try:
            is_alive = cache_backend.ping()
            if is_alive:
                stats = cache_backend.get_stats()
                return {
                    "status": "healthy",
                    "details": {
                        "backend": stats.get("backend"),
                        "connected": True
                    }
                }
            else:
                return {
                    "status": "unhealthy",
                    "details": {"connected": False}
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "details": {"error": str(e)}
            }
    return check


def create_upstream_api_check(upstream_url: str) -> Callable:
    """Create upstream API health check function"""
    def check():
        try:
            import requests
            response = requests.get(
                f"{upstream_url}/character/1",
                timeout=5
            )
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "details": {"status_code": response.status_code}
                }
            else:
                return {
                    "status": "degraded",
                    "details": {"status_code": response.status_code}
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "details": {"error": str(e)}
            }
    return check
