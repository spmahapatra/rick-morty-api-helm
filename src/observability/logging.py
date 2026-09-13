"""Structured logging implementation"""

import logging
import json
import sys
from typing import Any, Optional, Dict
from datetime import datetime
import uuid

# Global correlation ID storage
_correlation_id = None


def set_correlation_id(cid: str) -> None:
    """Set correlation ID for current context"""
    global _correlation_id
    _correlation_id = cid


def get_correlation_id() -> str:
    """Get correlation ID or generate new one"""
    global _correlation_id
    if not _correlation_id:
        _correlation_id = str(uuid.uuid4())
    return _correlation_id


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_obj = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": get_correlation_id()
        }
        
        # Add custom fields
        if hasattr(record, "correlation_id"):
            log_obj["correlation_id"] = record.correlation_id
        
        if hasattr(record, "context"):
            log_obj.update(record.context)
        
        # Add exception info if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_obj)


class StructuredLogger:
    """Structured logging wrapper"""
    
    def __init__(self, name: str):
        """Initialize structured logger"""
        self.logger = logging.getLogger(name)
    
    def _log(self, level: int, message: str, **context) -> None:
        """Internal logging method"""
        extra = {"context": context} if context else {}
        self.logger.log(level, message, extra=extra)
    
    def debug(self, message: str, **context) -> None:
        """Log debug message"""
        self._log(logging.DEBUG, message, **context)
    
    def info(self, message: str, **context) -> None:
        """Log info message"""
        self._log(logging.INFO, message, **context)
    
    def warning(self, message: str, **context) -> None:
        """Log warning message"""
        self._log(logging.WARNING, message, **context)
    
    def error(self, message: str, **context) -> None:
        """Log error message"""
        self._log(logging.ERROR, message, **context)
    
    def critical(self, message: str, **context) -> None:
        """Log critical message"""
        self._log(logging.CRITICAL, message, **context)


def setup_logging(
    level: str = "INFO",
    format_type: str = "json",
    log_file: Optional[str] = None
) -> logging.Logger:
    """Setup logging configuration"""
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    if format_type.lower() == "json":
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(getattr(logging, level.upper()))
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except Exception as e:
            root_logger.error(f"Failed to create file handler: {e}")
    
    return root_logger
