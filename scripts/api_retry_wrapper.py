#!/usr/bin/env python3
"""
API Retry Wrapper with Exponential Backoff and Rate Limiting
Provides robust error handling for API calls with automatic retry logic.

Author: AGI Hackathon Team
Date: 2026-04-15
"""

import time
import threading
from functools import wraps
from typing import Callable, Optional, Any
from collections import deque


class APIRateLimiter:
    """
    Rate limiter for API calls to prevent hitting rate limits.
    Implements token bucket algorithm.
    """

    def __init__(self, max_calls: int = 10, time_window: float = 60.0):
        """
        Initialize rate limiter.

        Args:
            max_calls: Maximum number of calls allowed in time window
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = deque()  # Stores timestamps of calls
        self.lock = threading.Lock()

    def wait_if_needed(self) -> float:
        """
        Wait if rate limit would be exceeded.

        Returns:
            Time waited in seconds
        """
        with self.lock:
            now = time.time()

            # Remove old calls outside time window
            while self.calls and now - self.calls[0] > self.time_window:
                self.calls.popleft()

            # Check if we can make another call
            if len(self.calls) >= self.max_calls:
                oldest_call = self.calls[0]
                wait_time = self.time_window - (now - oldest_call) + 0.1  # Small buffer
                print(f"  🕐 Rate limit reached. Waiting {wait_time:.1f}s...")
                time.sleep(wait_time)
                now = time.time()
                # Clean up again after waiting
                while self.calls and now - self.calls[0] > self.time_window:
                    self.calls.popleft()

            # Record this call
            self.calls.append(now)

            return 0

        return 0


class RetryConfig:
    """Configuration for retry behavior"""

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 10.0,
        backoff_factor: float = 2.0,
        jitter: float = 0.1,
        retryable_exceptions: tuple = (Exception,)
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions


# Default configurations for different APIs
API_CONFIGS = {
    'anthropic': RetryConfig(
        max_attempts=3,
        base_delay=1.0,
        max_delay=8.0,
        backoff_factor=2.0,
        retryable_exceptions=(Exception,)
    ),
    'openai': RetryConfig(
        max_attempts=3,
        base_delay=1.0,
        max_delay=10.0,
        backoff_factor=2.0,
        retryable_exceptions=(Exception,)
    ),
    'google': RetryConfig(
        max_attempts=3,
        base_delay=1.5,
        max_delay=12.0,
        backoff_factor=2.0,
        retryable_exceptions=(Exception,)
    ),
    'zhipu': RetryConfig(
        max_attempts=3,
        base_delay=2.0,
        max_delay=15.0,
        backoff_factor=2.0,
        retryable_exceptions=(Exception,)
    ),
}


def with_retry(
    api_name: str,
    rate_limiter: Optional[APIRateLimiter] = None,
    config: Optional[RetryConfig] = None
):
    """
    Decorator for retrying API calls with exponential backoff.

    Args:
        api_name: Name of API ('anthropic', 'openai', 'google', 'zhipu')
        rate_limiter: Optional rate limiter instance
        config: Optional retry configuration (uses defaults if not provided)

    Returns:
        Decorated function
    """
    if config is None:
        config = API_CONFIGS.get(api_name, API_CONFIGS['anthropic'])

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(1, config.max_attempts + 1):
                try:
                    # Apply rate limiting if provided
                    if rate_limiter:
                        rate_limiter.wait_if_needed()

                    # Make the API call
                    result = func(*args, **kwargs)
                    return result

                except config.retryable_exceptions as e:
                    last_exception = e

                    # Check if this is the last attempt
                    if attempt < config.max_attempts:
                        # Calculate delay with exponential backoff and jitter
                        delay = min(
                            config.base_delay * (config.backoff_factor ** (attempt - 1)),
                            config.max_delay
                        )

                        # Add jitter (random variation)
                        import random
                        jitter_amount = delay * config.jitter
                        jittered_delay = delay + (random.random() * jitter_amount * 2 - jitter_amount)

                        print(f"  🔄 Attempt {attempt}/{config.max_attempts} failed: {str(e)[:100]}")
                        print(f"     Retrying in {jittered_delay:.2f}s...")

                        time.sleep(jittered_delay)
                    else:
                        print(f"  ❌ All {config.max_attempts} attempts failed for {api_name}")
                        print(f"     Last error: {str(e)[:200]}")

            # Re-raise the last exception if all attempts failed
            raise last_exception

        return wrapper

    return decorator


def call_with_retry(
    func: Callable,
    api_name: str,
    rate_limiter: Optional[APIRateLimiter] = None,
    config: Optional[RetryConfig] = None,
    *args,
    **kwargs
) -> Any:
    """
    Alternative function-based API for calling with retry logic.
    Useful when decorator is not suitable.

    Args:
        func: Function to call
        api_name: Name of API
        rate_limiter: Optional rate limiter
        config: Optional retry configuration
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Result of function call
    """
    retry_decorator = with_retry(api_name, rate_limiter, config)
    decorated_func = retry_decorator(func)
    return decorated_func(*args, **kwargs)


# Circuit breaker pattern for preventing cascading failures
class CircuitBreaker:
    """
    Circuit breaker to prevent cascading failures.
    Opens circuit after too many failures and closes after recovery timeout.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        name: str = "default"
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Time in seconds before attempting recovery
            name: Name of this circuit breaker (for logging)
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed = normal, open = refusing calls
        self.lock = threading.Lock()

    def record_success(self):
        """Record a successful call"""
        with self.lock:
            self.failures = max(0, self.failures - 1)
            if self.failures == 0 and self.state == "open":
                print(f"  🔓 Circuit '{self.name}' recovered after {self.recovery_timeout}s timeout")
                self.state = "closed"

    def record_failure(self):
        """Record a failed call"""
        with self.lock:
            self.failures += 1
            self.last_failure_time = time.time()

            if self.failures >= self.failure_threshold and self.state == "closed":
                print(f"  🚫 Circuit '{self.name}' opened after {self.failures} failures")
                self.state = "open"

    def allow_request(self) -> bool:
        """
        Check if request should be allowed through circuit breaker.

        Returns:
            True if request allowed, False otherwise
        """
        with self.lock:
            if self.state == "open":
                # Check if recovery timeout has passed
                if (self.last_failure_time and
                    time.time() - self.last_failure_time > self.recovery_timeout):
                    print(f"  🔓 Circuit '{self.name}' attempting to recover...")
                    self.state = "half-open"
                    return True
                else:
                    return False
            elif self.state == "half-open":
                # Allow one request to test
                return True
            else:  # closed
                return True

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.

        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Result of function call

        Raises:
            CircuitOpenError if circuit is open
        """
        if not self.allow_request():
            raise CircuitOpenError(f"Circuit '{self.name}' is open due to {self.failures} failures")

        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise


class CircuitOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass


def test_retry_wrapper():
    """Test the retry wrapper with simulated failures"""

    @with_retry('test_api', config=RetryConfig(max_attempts=3))
    def simulated_api_call(attempt_num=1):
        """Simulated API that fails twice then succeeds"""
        if attempt_num < 3:
            raise Exception(f"Simulated API failure (attempt {attempt_num})")
        return "Success!"

    print("Testing Retry Wrapper")
    print("=" * 50)

    # Test with rate limiter
    limiter = APIRateLimiter(max_calls=2, time_window=1.0)

    for i in range(1, 6):
        print(f"\nCall {i}:")
        try:
            result = call_with_retry(simulated_api_call, 'test_api', rate_limiter=limiter,
                                  attempt_num=i)
            print(f"  ✅ Success: {result}")
        except Exception as e:
            print(f"  ❌ Failed: {e}")


def test_circuit_breaker():
    """Test circuit breaker"""

    print("\n\nTesting Circuit Breaker")
    print("=" * 50)

    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=5.0, name="test")

    @with_retry('test_api', config=RetryConfig(max_attempts=2))
    def flaky_api(fail_times=2):
        """Simulated flaky API"""
        import random
        if random.random() < 0.6:  # 60% failure rate
            raise Exception("Simulated random failure")
        return "Success"

    print(f"Initial state: {breaker.state}")
    print(f"Failure threshold: {breaker.failure_threshold}")

    for i in range(1, 8):
        print(f"\nAttempt {i}:")
        try:
            result = breaker.execute(flaky_api)
            print(f"  ✅ Success: {result} (State: {breaker.state})")
        except CircuitOpenError as e:
            print(f"  🚫 Circuit Open: {e}")
        except Exception as e:
            print(f"  ❌ API Error: {e} (State: {breaker.state})")


if __name__ == "__main__":
    test_retry_wrapper()
    test_circuit_breaker()
