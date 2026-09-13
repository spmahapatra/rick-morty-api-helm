"""Tests for observability module"""

import pytest
import json
import logging
from src.observability import StructuredLogger, setup_logging, HealthChecker, MetricsCollector
from src.observability.logging import set_correlation_id, get_correlation_id


class TestStructuredLogging:
    """Test structured logging"""
    
    def test_correlation_id_management(self):
        """Test correlation ID management"""
        test_id = "test-123-456"
        set_correlation_id(test_id)
        assert get_correlation_id() == test_id
    
    def test_structured_logger_creation(self):
        """Test logger creation"""
        logger = StructuredLogger("test_logger")
        assert logger.logger.name == "test_logger"
    
    def test_logger_methods_exist(self):
        """Test all logger methods exist"""
        logger = StructuredLogger("test_logger")
        assert hasattr(logger, "debug")
        assert hasattr(logger, "info")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "error")
        assert hasattr(logger, "critical")


class TestHealthChecker:
    """Test health check functionality"""
    
    def test_register_check(self):
        """Test registering health checks"""
        checker = HealthChecker()
        
        def test_check():
            return {"status": "healthy"}
        
        checker.register_check("test", test_check)
        assert "test" in checker.checks
    
    def test_perform_single_check(self):
        """Test performing single health check"""
        checker = HealthChecker()
        
        def test_check():
            return {"status": "healthy", "details": {"connected": True}}
        
        checker.register_check("test", test_check)
        result = checker.perform_check("test")
        
        assert result["status"] == "healthy"
        assert "latency_ms" in result
        assert result["details"]["connected"] is True
    
    def test_perform_all_checks(self):
        """Test performing all health checks"""
        checker = HealthChecker()
        
        def check1():
            return {"status": "healthy"}
        
        def check2():
            return {"status": "healthy"}
        
        checker.register_check("check1", check1)
        checker.register_check("check2", check2)
        
        result = checker.perform_all_checks()
        
        assert result["status"] == "healthy"
        assert "checks" in result
        assert "check1" in result["checks"]
        assert "check2" in result["checks"]
    
    def test_critical_failure_detection(self):
        """Test detection of critical failures"""
        checker = HealthChecker()
        
        def healthy_check():
            return {"status": "healthy"}
        
        def failing_check():
            return {"status": "unhealthy", "error": "Connection failed"}
        
        checker.register_check("database", failing_check)
        checker.register_check("cache", healthy_check)
        
        result = checker.perform_all_checks()
        
        # Database is critical, so overall status is unhealthy
        assert result["status"] == "unhealthy"
        assert "database" in result["critical_failures"]
    
    def test_check_error_handling(self):
        """Test error handling in health checks"""
        checker = HealthChecker()
        
        def failing_check():
            raise RuntimeError("Check failed")
        
        checker.register_check("failing", failing_check)
        result = checker.perform_check("failing")
        
        assert result["status"] == "unhealthy"
        assert "error" in result
    
    def test_nonexistent_check(self):
        """Test requesting nonexistent check"""
        checker = HealthChecker()
        result = checker.perform_check("nonexistent")
        
        assert result["status"] == "unknown"
        assert "error" in result


class TestMetricsCollector:
    """Test metrics collection"""
    
    def test_initialization(self):
        """Test metrics collector initialization"""
        collector = MetricsCollector("unique_app_1")
        assert collector.app_name == "unique_app_1"
    
    def test_record_request(self):
        """Test recording request metrics"""
        collector = MetricsCollector("unique_app_2")
        # Just verify the method exists and doesn't raise
        try:
            collector.record_request("GET", "/api/test", 200, 0.5)
            # If we get here without error in method signature, test passes
            assert True
        except TypeError:
            pytest.fail("record_request method has unexpected signature")
    
    def test_record_cache_metrics(self):
        """Test recording cache metrics"""
        # Use unique collector per test to avoid prometheus registry conflicts
        collector = MetricsCollector("unique_app_3")
        try:
            collector.record_cache_hit("redis")
            collector.record_cache_miss("redis")
            collector.record_cache_error("redis")
            assert True
        except TypeError:
            pytest.fail("Cache metric methods have unexpected signature")
    
    def test_record_error(self):
        """Test recording error metrics"""
        collector = MetricsCollector("unique_app_4")
        try:
            collector.record_error("ValueError", "/api/test")
            assert True
        except TypeError:
            pytest.fail("record_error method has unexpected signature")
