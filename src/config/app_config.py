"""
Configuration file for Rick and Morty Character API
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration"""
    DEBUG = False
    TESTING = False
    FLASK_ENV = "production"
    
    # Rick and Morty API
    RICK_AND_MORTY_API_BASE_URL = os.getenv(
        "RICK_AND_MORTY_API_BASE_URL",
        "https://rickandmortyapi.com/api"
    )
    
    # Pagination
    DEFAULT_PAGE = 1
    DEFAULT_LIMIT = 10
    MAX_LIMIT = 50
    
    # Filters
    SPECIES_FILTER = "human"
    STATUS_FILTER = "alive"
    ORIGIN_VARIANTS = [
        "earth (c-137)",
        "earth (replacement dimension)",
        "earth",
    ]
    
    # Timeout
    REQUEST_TIMEOUT = 10
    
    # Cache configuration
    CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", 300))
    
    # Redis configuration
    REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = "development"
    CACHE_ENABLED = False  # Use in-memory cache for development


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    FLASK_ENV = "testing"
    CACHE_ENABLED = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = "production"
    CACHE_ENABLED = True  # Use Redis in production


# Select configuration based on environment
config_name = os.getenv("FLASK_ENV", "development").lower()
if config_name == "testing":
    config = TestingConfig()
elif config_name == "production":
    config = ProductionConfig()
else:
    config = DevelopmentConfig()


# Cache backend initialization
_cache_backend = None


def get_cache_backend():
    """Get or initialize cache backend"""
    global _cache_backend
    
    if _cache_backend is not None:
        return _cache_backend
    
    if not config.CACHE_ENABLED:
        from src.cache.backend import InMemoryBackend
        _cache_backend = InMemoryBackend()
        logger = __import__('logging').getLogger(__name__)
        logger.warning("CACHE BACKEND: Using InMemoryBackend (CACHE_ENABLED=false)")
        return _cache_backend
    
    try:
        from src.cache.backend import RedisBackend
        _cache_backend = RedisBackend(
            url=config.REDIS_URL,
            pool_size=10,
            socket_timeout=5
        )
        logger = __import__('logging').getLogger(__name__)
        logger.warning(f"CACHE BACKEND: Using RedisBackend at {config.REDIS_URL}")
        return _cache_backend
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"CACHE BACKEND: Failed to initialize Redis backend: {e}")
        logger.warning("CACHE BACKEND: Falling back to InMemoryBackend (may not work with multiple workers)")
        
        from src.cache.backend import InMemoryBackend
        _cache_backend = InMemoryBackend()
        return _cache_backend

