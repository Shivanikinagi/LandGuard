"""
Rate limiting to prevent abuse and DoS attacks.
Supports per-IP, per-user, and per-endpoint rate limiting.
"""

import time
from typing import Dict, Optional, Tuple
from collections import defaultdict
from datetime import datetime, timedelta
from threading import Lock


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str, retry_after: int):
        """
        Initialize exception.
        
        Args:
            message: Error message
            retry_after: Seconds until rate limit resets
        """
        super().__init__(message)
        self.retry_after = retry_after


class RateLimiter:
    """Token bucket rate limiter with sliding window."""
    
    def __init__(
        self,
        max_requests: int = 100,
        window_seconds: int = 60,
        burst_size: Optional[int] = None
    ):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests allowed in the time window
            window_seconds: Time window in seconds
            burst_size: Maximum burst size (defaults to max_requests)
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.burst_size = burst_size or max_requests
        
        # Storage for request timestamps per identifier
        self._requests: Dict[str, list] = defaultdict(list)
        self._lock = Lock()
    
    def check_limit(self, identifier: str) -> Tuple[bool, Optional[int]]:
        """
        Check if request is within rate limit.
        
        Args:
            identifier: Unique identifier (IP, user_id, etc.)
            
        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        with self._lock:
            now = time.time()
            window_start = now - self.window_seconds
            
            # Get request history for this identifier
            requests = self._requests[identifier]
            
            # Remove requests outside the time window
            requests[:] = [req_time for req_time in requests if req_time > window_start]
            
            # Check if under limit
            if len(requests) < self.max_requests:
                requests.append(now)
                return True, None
            
            # Calculate retry_after
            oldest_request = min(requests)
            retry_after = int(oldest_request + self.window_seconds - now) + 1
            
            return False, retry_after
    
    def check_and_raise(self, identifier: str):
        """
        Check rate limit and raise exception if exceeded.
        
        Args:
            identifier: Unique identifier
            
        Raises:
            RateLimitExceeded: If rate limit exceeded
        """
        is_allowed, retry_after = self.check_limit(identifier)
        
        if not is_allowed:
            raise RateLimitExceeded(
                f"Rate limit exceeded. Try again in {retry_after} seconds.",
                retry_after=retry_after
            )
    
    def reset(self, identifier: str):
        """
        Reset rate limit for an identifier.
        
        Args:
            identifier: Unique identifier to reset
        """
        with self._lock:
            if identifier in self._requests:
                del self._requests[identifier]
    
    def get_remaining(self, identifier: str) -> int:
        """
        Get remaining requests for an identifier.
        
        Args:
            identifier: Unique identifier
            
        Returns:
            Number of remaining requests
        """
        with self._lock:
            now = time.time()
            window_start = now - self.window_seconds
            
            requests = self._requests[identifier]
            requests[:] = [req_time for req_time in requests if req_time > window_start]
            
            return max(0, self.max_requests - len(requests))
    
    def cleanup(self, max_age_seconds: int = 3600):
        """
        Clean up old entries to prevent memory leaks.
        
        Args:
            max_age_seconds: Remove identifiers not seen in this many seconds
        """
        with self._lock:
            now = time.time()
            cutoff = now - max_age_seconds
            
            identifiers_to_remove = []
            
            for identifier, requests in self._requests.items():
                if not requests or max(requests) < cutoff:
                    identifiers_to_remove.append(identifier)
            
            for identifier in identifiers_to_remove:
                del self._requests[identifier]


class MultiTierRateLimiter:
    """Rate limiter with multiple tiers (per-IP, per-user, per-endpoint)."""
    
    def __init__(self):
        """Initialize multi-tier rate limiter with default limits."""
        # Global rate limit (all requests)
        self.global_limiter = RateLimiter(
            max_requests=1000,
            window_seconds=60
        )
        
        # Per-IP rate limit
        self.ip_limiter = RateLimiter(
            max_requests=100,
            window_seconds=60
        )
        
        # Per-user rate limit
        self.user_limiter = RateLimiter(
            max_requests=200,
            window_seconds=60
        )
        
        # Per-endpoint rate limits
        self.endpoint_limiters: Dict[str, RateLimiter] = {
            'analyze': RateLimiter(max_requests=50, window_seconds=60),
            'upload': RateLimiter(max_requests=20, window_seconds=60),
            'batch': RateLimiter(max_requests=10, window_seconds=60),
        }
    
    def check_request(
        self,
        ip_address: str,
        user_id: Optional[str] = None,
        endpoint: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Check all applicable rate limits.
        
        Args:
            ip_address: Client IP address
            user_id: User identifier (optional)
            endpoint: Endpoint name (optional)
            
        Returns:
            Tuple of (is_allowed, error_message)
        """
        # Check global limit
        is_allowed, retry_after = self.global_limiter.check_limit('global')
        if not is_allowed:
            return False, f"Global rate limit exceeded. Retry after {retry_after}s"
        
        # Check IP limit
        is_allowed, retry_after = self.ip_limiter.check_limit(ip_address)
        if not is_allowed:
            return False, f"IP rate limit exceeded. Retry after {retry_after}s"
        
        # Check user limit if user_id provided
        if user_id:
            is_allowed, retry_after = self.user_limiter.check_limit(user_id)
            if not is_allowed:
                return False, f"User rate limit exceeded. Retry after {retry_after}s"
        
        # Check endpoint limit if endpoint provided
        if endpoint and endpoint in self.endpoint_limiters:
            limiter = self.endpoint_limiters[endpoint]
            is_allowed, retry_after = limiter.check_limit(f"{ip_address}:{endpoint}")
            if not is_allowed:
                return False, f"Endpoint rate limit exceeded. Retry after {retry_after}s"
        
        return True, None
    
    def get_limits_info(
        self,
        ip_address: str,
        user_id: Optional[str] = None,
        endpoint: Optional[str] = None
    ) -> Dict[str, Dict[str, int]]:
        """
        Get rate limit information.
        
        Args:
            ip_address: Client IP address
            user_id: User identifier (optional)
            endpoint: Endpoint name (optional)
            
        Returns:
            Dictionary with limit information
        """
        info = {
            'global': {
                'limit': self.global_limiter.max_requests,
                'remaining': self.global_limiter.get_remaining('global'),
                'window': self.global_limiter.window_seconds
            },
            'ip': {
                'limit': self.ip_limiter.max_requests,
                'remaining': self.ip_limiter.get_remaining(ip_address),
                'window': self.ip_limiter.window_seconds
            }
        }
        
        if user_id:
            info['user'] = {
                'limit': self.user_limiter.max_requests,
                'remaining': self.user_limiter.get_remaining(user_id),
                'window': self.user_limiter.window_seconds
            }
        
        if endpoint and endpoint in self.endpoint_limiters:
            limiter = self.endpoint_limiters[endpoint]
            info['endpoint'] = {
                'limit': limiter.max_requests,
                'remaining': limiter.get_remaining(f"{ip_address}:{endpoint}"),
                'window': limiter.window_seconds
            }
        
        return info
    
    def cleanup_all(self):
        """Clean up all rate limiters."""
        self.global_limiter.cleanup()
        self.ip_limiter.cleanup()
        self.user_limiter.cleanup()
        
        for limiter in self.endpoint_limiters.values():
            limiter.cleanup()


class AdaptiveRateLimiter(RateLimiter):
    """Rate limiter that adapts based on system load."""
    
    def __init__(
        self,
        base_requests: int = 100,
        window_seconds: int = 60,
        min_requests: int = 10,
        max_requests: int = 500
    ):
        """
        Initialize adaptive rate limiter.
        
        Args:
            base_requests: Base rate limit
            window_seconds: Time window in seconds
            min_requests: Minimum rate limit
            max_requests: Maximum rate limit
        """
        super().__init__(base_requests, window_seconds)
        self.base_requests = base_requests
        self.min_requests = min_requests
        self.max_requests = max_requests
        self.current_load = 0.0  # 0.0 to 1.0
    
    def update_load(self, load: float):
        """
        Update system load factor.
        
        Args:
            load: Load factor (0.0 = idle, 1.0 = overloaded)
        """
        self.current_load = max(0.0, min(1.0, load))
        
        # Adjust max_requests based on load
        # High load = lower limits
        adjustment_factor = 1.0 - (self.current_load * 0.8)
        
        self.max_requests = int(
            max(
                self.min_requests,
                min(
                    self.max_requests,
                    self.base_requests * adjustment_factor
                )
            )
        )
    
    def get_load_info(self) -> Dict[str, any]:
        """
        Get current load information.
        
        Returns:
            Dictionary with load and limit information
        """
        return {
            'current_load': self.current_load,
            'base_limit': self.base_requests,
            'current_limit': self.max_requests,
            'min_limit': self.min_requests,
            'max_limit': self.max_requests
        }