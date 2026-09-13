"""Tests for resilience layer"""

import pytest
import time
from src.resilience import RetryPolicy, CircuitBreaker, RateLimiter, CircuitBreakerOpenError, RateLimitExceeded


class TestRetryPolicy:
    """Test retry logic"""
    
    def test_successful_on_first_attempt(self):
        """Test successful execution on first attempt"""
        policy = RetryPolicy(max_attempts=3)
        call_count = 0
        
        def successful_func():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = policy.execute(successful_func)
        assert result == "success"
        assert call_count == 1
    
    def test_retry_on_failure(self):
        """Test retry on transient failure"""
        policy = RetryPolicy(max_attempts=3, base_delay=0.1)
        call_count = 0
        
        def failing_then_success():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Transient failure")
            return "success"
        
        result = policy.execute(failing_then_success)
        assert result == "success"
        assert call_count == 3
    
    def test_max_attempts_exceeded(self):
        """Test exception after max attempts"""
        policy = RetryPolicy(max_attempts=2)
        call_count = 0
        
        def always_fails():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError):
            policy.execute(always_fails)
        
        assert call_count == 2
    
    def test_exponential_backoff_calculation(self):
        """Test exponential backoff calculation"""
        policy = RetryPolicy(
            max_attempts=5,
            base_delay=1.0,
            max_delay=60.0,
            jitter=False
        )
        
        # Check delay calculations (without jitter)
        assert policy.calculate_delay(0) == 1.0  # 1 * 2^0
        assert policy.calculate_delay(1) == 2.0  # 1 * 2^1
        assert policy.calculate_delay(2) == 4.0  # 1 * 2^2
        assert policy.calculate_delay(3) == 8.0  # 1 * 2^3
        assert policy.calculate_delay(4) == 16.0  # 1 * 2^4


class TestCircuitBreaker:
    """Test circuit breaker pattern"""
    
    def test_closed_state_success(self):
        """Test circuit breaker in CLOSED state with successful call"""
        breaker = CircuitBreaker(
            name="test",
            failure_threshold=3,
            reset_timeout_s=60
        )
        
        def successful_func():
            return "success"
        
        result = breaker.call(successful_func)
        assert result == "success"
        assert breaker.get_state() == "CLOSED"
    
    def test_open_state_rejects_calls(self):
        """Test circuit breaker opens after threshold"""
        breaker = CircuitBreaker(
            name="test",
            failure_threshold=2,
            reset_timeout_s=60,
            expected_exception=ValueError
        )
        
        def failing_func():
            raise ValueError("Failure")
        
        # First failure
        with pytest.raises(ValueError):
            breaker.call(failing_func)
        assert breaker.get_state() == "CLOSED"
        
        # Second failure opens circuit
        with pytest.raises(ValueError):
            breaker.call(failing_func)
        assert breaker.get_state() == "OPEN"
        
        # Further calls rejected immediately
        with pytest.raises(CircuitBreakerOpenError):
            breaker.call(failing_func)
    
    def test_half_open_recovery(self):
        """Test circuit breaker recovery through HALF_OPEN"""
        breaker = CircuitBreaker(
            name="test",
            failure_threshold=1,
            reset_timeout_s=0.1,  # Short timeout for testing
            expected_exception=ValueError
        )
        
        def failing_func():
            raise ValueError("Failure")
        
        # Open the circuit
        with pytest.raises(ValueError):
            breaker.call(failing_func)
        assert breaker.get_state() == "OPEN"
        
        # Wait for reset timeout
        time.sleep(0.15)
        
        # Next call attempts recovery
        def successful_func():
            return "success"
        
        result = breaker.call(successful_func)
        assert result == "success"
        assert breaker.get_state() == "CLOSED"
    
    def test_manual_reset(self):
        """Test manual circuit breaker reset"""
        breaker = CircuitBreaker(failure_threshold=1)
        
        def failing_func():
            raise ValueError("Failure")
        
        # Open circuit
        with pytest.raises(ValueError):
            breaker.call(failing_func)
        assert breaker.get_state() == "OPEN"
        
        # Manual reset
        breaker.reset()
        assert breaker.get_state() == "CLOSED"


class TestRateLimiter:
    """Test rate limiting"""
    
    def test_rate_limit_within_limit(self):
        """Test requests within rate limit"""
        limiter = RateLimiter(limit_per_minute=10)
        
        for i in range(10):
            result = limiter.check_rate_limit("consumer_1")
            assert result['allowed'] is True
            assert result['remaining'] == 10 - (i + 1)
    
    def test_rate_limit_exceeded(self):
        """Test rate limit exceeded"""
        limiter = RateLimiter(limit_per_minute=3)
        
        # First 3 requests allowed
        for i in range(3):
            result = limiter.check_rate_limit("consumer_1")
            assert result['allowed'] is True
        
        # 4th request rejected
        result = limiter.check_rate_limit("consumer_1")
        assert result['allowed'] is False
        assert result['retry_after_s'] > 0
    
    def test_rate_limit_different_consumers(self):
        """Test rate limiting per consumer"""
        limiter = RateLimiter(limit_per_minute=2)
        
        # Consumer 1: 2 requests
        result1 = limiter.check_rate_limit("consumer_1")
        assert result1['allowed'] is True
        result1 = limiter.check_rate_limit("consumer_1")
        assert result1['allowed'] is True
        
        # Consumer 1: 3rd request rejected
        result1 = limiter.check_rate_limit("consumer_1")
        assert result1['allowed'] is False
        
        # Consumer 2: Not limited
        result2 = limiter.check_rate_limit("consumer_2")
        assert result2['allowed'] is True
    
    def test_rate_limit_reset(self):
        """Test rate limit reset"""
        limiter = RateLimiter(limit_per_minute=2)
        
        # Hit limit
        limiter.check_rate_limit("consumer_1")
        limiter.check_rate_limit("consumer_1")
        result = limiter.check_rate_limit("consumer_1")
        assert result['allowed'] is False
        
        # Reset consumer
        limiter.reset("consumer_1")
        
        # Now allowed again
        result = limiter.check_rate_limit("consumer_1")
        assert result['allowed'] is True
    
    def test_is_rate_limited(self):
        """Test is_rate_limited helper"""
        limiter = RateLimiter(limit_per_minute=1)
        
        assert limiter.is_rate_limited("consumer_1") is False
        limiter.check_rate_limit("consumer_1")
        
        # 2nd request should be limited
        assert limiter.is_rate_limited("consumer_1") is True
