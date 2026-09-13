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
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import OperationalError, ProgrammingError

# Add parent directory to path so we can import src
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database.models import Base
from src.observability.logging import setup_logging, StructuredLogger

# Setup logging
setup_logging()
logger = StructuredLogger(__name__)


def init_database():
    """
    Initialize the database by creating all tables.
    
    This function:
    1. Gets the database URL from environment
    2. Creates a connection to the database
    3. Creates all tables (idempotent)
    4. Returns True if successful, False otherwise
    
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
    
    logger.info(
        "Starting database initialization",
        context={
            "database_url": database_url.replace(database_url.split("@")[1], "****") if "@" in database_url else "****",
            "action": "init_database"
        }
    )
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Test connection
        logger.info("Testing database connection")
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info(
            "Database connection successful",
            context={"connection_test": "passed"}
        )
        
        # Check which tables already exist
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        logger.info(
            "Checking existing tables",
            context={"existing_tables": existing_tables}
        )
        
        # Create all tables (idempotent)
        Base.metadata.create_all(bind=engine)
        logger.info(
            "Database tables created/verified",
            context={
                "action": "create_all",
                "status": "success"
            }
        )
        
        # Verify tables were created
        inspector = inspect(engine)
        created_tables = inspector.get_table_names()
        logger.info(
            "Final table verification",
            context={
                "tables_present": created_tables,
                "table_count": len(created_tables)
            }
        )
        
        # Close engine
        engine.dispose()
        
        logger.info(
            "Database initialization completed successfully",
            context={
                "status": "complete",
                "tables": created_tables
            }
        )
        
        return True
        
    except OperationalError as e:
        logger.error(
            "Database operational error",
            error_type="OperationalError",
            error_message=str(e),
            context={
                "action": "init_database",
                "phase": "connection"
            }
        )
        return False
        
    except ProgrammingError as e:
        logger.error(
            "Database programming error",
            error_type="ProgrammingError",
            error_message=str(e),
            context={
                "action": "init_database",
                "phase": "table_creation"
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
                "exception": str(e)
            }
        )
        return False


if __name__ == "__main__":
    """
    Run database initialization.
    
    Exit codes:
        0 - Success
        1 - Failure
    """
    success = init_database()
    sys.exit(0 if success else 1)
