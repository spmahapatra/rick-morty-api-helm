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


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = "development"


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    FLASK_ENV = "testing"


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = "production"


# Select configuration based on environment
config_name = os.getenv("FLASK_ENV", "development").lower()
if config_name == "testing":
    config = TestingConfig()
elif config_name == "production":
    config = ProductionConfig()
else:
    config = DevelopmentConfig()
