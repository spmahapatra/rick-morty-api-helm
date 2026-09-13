"""Retry logic with exponential backoff and jitter"""

import time
import random
import logging
from typing import Callable, Any, Type, Tuple
from functools import wraps

logger = logging.getLogger(__name__)


class RetryPolicy:
    """Retry policy with exponential backoff"""
    
    def __init__(
        self,
        max_attempts: int = 5,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        jitter: bool = True,
        exceptions: Tuple[Type[Exception], ...] = (Exception,)
    ):
        """Initialize retry policy"""
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter
        self.exceptions = exceptions
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number"""
        # Exponential backoff: delay = min(base * 2^attempt, max)
        delay = min(self.base_delay * (2 ** attempt), self.max_delay)
        
        # Add jitter to prevent thundering herd
        if self.jitter:
            jitter_factor = random.uniform(0.8, 1.2)
            delay = delay * jitter_factor
        
        return delay
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic"""
        last_exception = None
        
        for attempt in range(self.max_attempts):
            try:
                return func(*args, **kwargs)
            except self.exceptions as e:
                last_exception = e
                
                if attempt < self.max_attempts - 1:
                    delay = self.calculate_delay(attempt)
                    logger.warning(
                        f"Attempt {attempt + 1}/{self.max_attempts} failed: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    time.sleep(delay)
                else:
                    logger.error(
                        f"All {self.max_attempts} attempts failed: {e}"
                    )
        
        raise last_exception
    
    def decorator(self):
        """Return decorator for easy use"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return self.execute(func, *args, **kwargs)
            return wrapper
        return decorator
