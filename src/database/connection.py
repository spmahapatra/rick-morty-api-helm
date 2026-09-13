"""Database connection management"""

from sqlalchemy import create_engine, event, pool
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Database connection manager with pooling"""
    
    def __init__(
        self,
        database_url: str,
        pool_size: int = 5,
        max_overflow: int = 10,
        pool_timeout: int = 30,
        echo: bool = False
    ):
        """Initialize database connection"""
        self.database_url = database_url
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        
        # Create engine with connection pooling
        self.engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            pool_pre_ping=True,  # Test connections before using
            echo=echo
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        # Add logging for connection events
        @event.listens_for(self.engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            logger.debug(f"Database connection opened: {dbapi_conn}")
        
        @event.listens_for(self.engine, "close")
        def receive_close(dbapi_conn, connection_record):
            logger.debug(f"Database connection closed: {dbapi_conn}")
        
        @event.listens_for(self.engine, "checkin")
        def receive_checkin(dbapi_conn, connection_record):
            logger.debug(f"Connection returned to pool: {dbapi_conn}")
        
        @event.listens_for(self.engine, "checkout")
        def receive_checkout(dbapi_conn, connection_record, connection_proxy):
            logger.debug(f"Connection obtained from pool: {dbapi_conn}")
        
        logger.info(f"Database connection initialized: {self.database_url}")
    
    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()
    
    def test_connection(self) -> bool:
        """Test database connectivity"""
        try:
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            logger.info("Database connection test passed")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def close(self) -> None:
        """Close all connections"""
        self.engine.dispose()
        logger.info("Database connections closed")
    
    def get_pool_status(self) -> dict:
        """Get connection pool status"""
        pool = self.engine.pool
        return {
            "pool_size": self.pool_size,
            "max_overflow": self.max_overflow,
            "pool_timeout": self.pool_timeout,
            "connections_in_pool": pool.size() if hasattr(pool, "size") else "N/A",
            "connections_checked_out": pool.checkedout() if hasattr(pool, "checkedout") else "N/A"
        }
