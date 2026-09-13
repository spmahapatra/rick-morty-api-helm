"""Tests for config module"""

import pytest
import os
from src.config import Settings


class TestSettings:
    """Test configuration settings"""
    
    def test_default_settings(self):
        """Test default settings"""
        settings = Settings()
        assert settings.FLASK_ENV == "development"
        assert settings.REDIS_POOL_SIZE == 10
        assert settings.DATABASE_POOL_SIZE == 5
    
    def test_redis_pool_size(self):
        """Test redis pool size configuration"""
        settings = Settings()
        assert settings.REDIS_POOL_SIZE == 10
    
    def test_database_configuration(self):
        """Test database configuration"""
        settings = Settings()
        assert settings.DATABASE_POOL_SIZE == 5
        assert settings.DATABASE_MAX_OVERFLOW == 10
        assert settings.DATABASE_POOL_TIMEOUT == 30
    
    def test_cache_configuration(self):
        """Test cache configuration"""
        settings = Settings()
        assert settings.CACHE_DEFAULT_TTL == 3600
        assert settings.CACHE_COLLECTION_TTL == 300
        assert settings.CACHE_INDIVIDUAL_TTL == 3600
    
    def test_rate_limit_configuration(self):
        """Test rate limiting configuration"""
        settings = Settings()
        assert settings.RATE_LIMIT_PUBLIC == 100
        assert settings.RATE_LIMIT_STANDARD == 1000
        assert settings.RATE_LIMIT_PREMIUM == 5000
    
    def test_resilience_configuration(self):
        """Test resilience configuration"""
        settings = Settings()
        assert settings.RETRY_MAX_ATTEMPTS == 5
        assert settings.CIRCUIT_BREAKER_THRESHOLD == 5
        assert settings.CIRCUIT_BREAKER_RESET_TIMEOUT == 60
