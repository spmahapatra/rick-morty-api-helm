"""Application settings and configuration"""

import os
from pydantic import BaseModel
from typing import Optional


class Settings(BaseModel):
    """Application configuration settings"""
    
    # Flask
    FLASK_ENV: str = os.getenv("FLASK_ENV", "development")
    FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-prod")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_POOL_SIZE: int = int(os.getenv("REDIS_POOL_SIZE", "10"))
    REDIS_SOCKET_TIMEOUT: int = int(os.getenv("REDIS_SOCKET_TIMEOUT", "5"))
    REDIS_ENABLE_CACHE: bool = os.getenv("REDIS_ENABLE_CACHE", "True").lower() == "true"
    
    # PostgreSQL
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://admin:password@localhost:5432/rickmorty")
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "5"))
    DATABASE_MAX_OVERFLOW: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))
    DATABASE_POOL_TIMEOUT: int = int(os.getenv("DATABASE_POOL_TIMEOUT", "30"))
    DATABASE_ECHO: bool = os.getenv("DATABASE_ECHO", "False").lower() == "true"
    
    # Caching
    CACHE_DEFAULT_TTL: int = int(os.getenv("CACHE_DEFAULT_TTL", "3600"))  # 1 hour
    CACHE_COLLECTION_TTL: int = int(os.getenv("CACHE_COLLECTION_TTL", "300"))  # 5 minutes
    CACHE_INDIVIDUAL_TTL: int = int(os.getenv("CACHE_INDIVIDUAL_TTL", "3600"))  # 1 hour
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"
    RATE_LIMIT_PUBLIC: int = int(os.getenv("RATE_LIMIT_PUBLIC", "100"))  # requests per minute
    RATE_LIMIT_STANDARD: int = int(os.getenv("RATE_LIMIT_STANDARD", "1000"))
    RATE_LIMIT_PREMIUM: int = int(os.getenv("RATE_LIMIT_PREMIUM", "5000"))
    
    # Resilience
    RETRY_MAX_ATTEMPTS: int = int(os.getenv("RETRY_MAX_ATTEMPTS", "5"))
    RETRY_BASE_DELAY: float = float(os.getenv("RETRY_BASE_DELAY", "1.0"))
    RETRY_MAX_DELAY: float = float(os.getenv("RETRY_MAX_DELAY", "60.0"))
    CIRCUIT_BREAKER_THRESHOLD: int = int(os.getenv("CIRCUIT_BREAKER_THRESHOLD", "5"))
    CIRCUIT_BREAKER_RESET_TIMEOUT: int = int(os.getenv("CIRCUIT_BREAKER_RESET_TIMEOUT", "60"))
    
    # Timeouts
    UPSTREAM_API_TIMEOUT: int = int(os.getenv("UPSTREAM_API_TIMEOUT", "10"))
    DATABASE_TIMEOUT: int = int(os.getenv("DATABASE_TIMEOUT", "30"))
    CACHE_TIMEOUT: int = int(os.getenv("CACHE_TIMEOUT", "5"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")  # json or text
    LOG_CORRELATION_ID: bool = os.getenv("LOG_CORRELATION_ID", "True").lower() == "true"
    
    # API
    RICK_AND_MORTY_API_BASE_URL: str = "https://rickandmortyapi.com/api"
    
    # Features
    ENABLE_PERSISTENCE: bool = os.getenv("ENABLE_PERSISTENCE", "True").lower() == "true"
    ENABLE_HEALTH_CHECK: bool = os.getenv("ENABLE_HEALTH_CHECK", "True").lower() == "true"
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "True").lower() == "true"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
