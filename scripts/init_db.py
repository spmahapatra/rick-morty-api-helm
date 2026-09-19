#!/usr/bin/env python
"""
Database initialization script - creates tables if they don't exist.

This script should be run before the Flask app starts to ensure all
required tables exist. It's idempotent - running it multiple times
is safe and won't recreate existing tables.
"""

import os
import logging
import sys
import time
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import OperationalError, ProgrammingError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Add parent directory to path so we can import src
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database.models import Base
from src.observability.logging import setup_logging, StructuredLogger

# Setup logging
setup_logging()
logger = StructuredLogger(__name__)


@retry(
    stop=stop_after_attempt(10),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(OperationalError),
    reraise=True
)
def create_engine_with_retry(database_url):
    """
    Create SQLAlchemy engine with automatic retry logic.
    
    Retries up to 10 times with exponential backoff (2-10 seconds)
    only on OperationalError (connection failures).
    
    Args:
        database_url: PostgreSQL connection URL
        
    Returns:
        SQLAlchemy Engine object
        
    Raises:
        OperationalError: If connection fails after all retries
    """
    engine = create_engine(database_url)
    
    # Test connection immediately
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    
    return engine


def validate_database_url(database_url):
    """
    Validate that the database URL is properly formatted.
    
    Args:
        database_url: PostgreSQL connection URL
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not database_url:
        logger.error(
            "Database URL validation failed",
            error_type="ConfigurationError",
            error_message="DATABASE_URL is empty",
            context={"check": "url_not_empty"}
        )
        return False
    
    if not database_url.startswith("postgresql://"):
        logger.error(
            "Database URL validation failed",
            error_type="ConfigurationError",
            error_message="DATABASE_URL must use postgresql:// protocol",
            context={"protocol": "postgresql://", "check": "correct_protocol"}
        )
        return False
    
    if "@" not in database_url:
        logger.error(
            "Database URL validation failed",
            error_type="ConfigurationError",
            error_message="DATABASE_URL must include credentials (user:password@host)",
            context={"check": "credentials_present"}
        )
        return False
    
    # Ensure database name is specified
    parts = database_url.split("/")
    if len(parts) < 4 or not parts[-1]:
        logger.error(
            "Database URL validation failed",
            error_type="ConfigurationError",
            error_message="DATABASE_URL must specify database name (host:port/database)",
            context={"check": "database_name_present"}
        )
        return False
    
    logger.info(
        "Database URL validation passed",
        context={"check": "format_valid"}
    )
    return True


def init_database():
    """
    Initialize the database by creating all tables.
    
    This function:
    1. Gets the database URL from environment
    2. Validates the connection string format
    3. Creates a connection to the database (with retry logic)
    4. Creates all tables (idempotent)
    5. Returns True if successful, False otherwise
    
    Returns:
        bool: True if initialization successful, False if failed
    """
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        logger.error(
            "Database initialization failed",
            error_type="ConfigurationError",
            error_message="DATABASE_URL environment variable not set",
            context={"environment_vars_checked": ["DATABASE_URL"]}
        )
        return False
    
    # Validate connection string format
    if not validate_database_url(database_url):
        return False
    
    # Mask sensitive information for logging
    masked_url = database_url.replace(database_url.split("@")[1], "****") if "@" in database_url else "****"
    
    logger.info(
        "Starting database initialization",
        context={
            "database_url": masked_url,
            "action": "init_database",
            "attempt": "1/10"
        }
    )
    
    engine = None
    try:
        # Create engine with retry logic
        logger.info(
            "Attempting to connect to database",
            context={
                "database_url": masked_url,
                "retry_strategy": "exponential_backoff_2_to_10s",
                "max_retries": 10
            }
        )
        
        engine = create_engine_with_retry(database_url)
        
        logger.info(
            "Database connection successful",
            context={"connection_test": "passed", "phase": "connection"}
        )
        
        # Check which tables already exist
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        logger.info(
            "Checking existing tables",
            context={
                "existing_tables": existing_tables,
                "table_count": len(existing_tables),
                "phase": "inspection"
            }
        )
        
        # Create all tables (idempotent)
        logger.info(
            "Creating database tables",
            context={
                "action": "create_all",
                "phase": "table_creation"
            }
        )
        
        Base.metadata.create_all(bind=engine)
        
        logger.info(
            "Database tables created/verified",
            context={
                "action": "create_all",
                "status": "success",
                "phase": "table_creation"
            }
        )
        
        # Verify tables were created
        inspector = inspect(engine)
        created_tables = inspector.get_table_names()
        
        logger.info(
            "Final table verification",
            context={
                "tables_present": created_tables,
                "table_count": len(created_tables),
                "phase": "verification",
                "required_tables": ["characters", "api_calls", "audit_logs", "cache_metadata"]
            }
        )
        
        # Close engine
        engine.dispose()
        
        logger.info(
            "Database initialization completed successfully",
            context={
                "status": "complete",
                "tables_count": len(created_tables),
                "tables": created_tables,
                "duration_phase": "initialization"
            }
        )
        
        return True
        
    except OperationalError as e:
        logger.error(
            "Database operational error - connection failed",
            error_type="OperationalError",
            error_message=str(e),
            context={
                "action": "init_database",
                "phase": "connection",
                "database_url": masked_url,
                "error_code": getattr(e, 'code', 'unknown')
            }
        )
        return False
        
    except ProgrammingError as e:
        logger.error(
            "Database programming error - SQL/schema issue",
            error_type="ProgrammingError",
            error_message=str(e),
            context={
                "action": "init_database",
                "phase": "table_creation",
                "error_code": getattr(e, 'code', 'unknown')
            }
        )
        return False
        
    except ModuleNotFoundError as e:
        logger.error(
            "Database driver not found",
            error_type="ModuleNotFoundError",
            error_message=str(e),
            context={
                "action": "init_database",
                "phase": "import",
                "missing_module": str(e),
                "solution": "Install psycopg2-binary: pip install psycopg2-binary"
            }
        )
        return False
        
    except Exception as e:
        logger.error(
            "Unexpected error during database initialization",
            error_type=type(e).__name__,
            error_message=str(e),
            context={
                "action": "init_database",
                "exception": str(e),
                "exception_type": type(e).__name__
            }
        )
        return False
        
    finally:
        # Ensure engine is disposed
        if engine:
            try:
                engine.dispose()
            except Exception as e:
                logger.warning(
                    "Warning during engine cleanup",
                    error_message=str(e),
                    context={"phase": "cleanup"}
                )


if __name__ == "__main__":
    """
    Run database initialization.
    
    Exit codes:
        0 - Success
        1 - Failure
    """
    success = init_database()
    sys.exit(0 if success else 1)
