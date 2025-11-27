"""
LandGuard Phase 11: HTTP Client Utility
Robust HTTP client with retry logic, rate limiting, and caching
"""

import requests
import time
import logging
from typing import Dict, Any, Optional, Literal
from datetime import datetime, timedelta
import json
from functools import wraps


logger = logging.getLogger(__name__)


class HTTPClient:
    """
    HTTP client with built-in retry logic, rate limiting, and error handling
    """
    
    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: int = 1
    ):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': 'LandGuard/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # Add API key to headers if provided
        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint"""
        endpoint = endpoint.lstrip('/')
        return f"{self.base_url}/{endpoint}"
    
    def _should_retry(self, status_code: int, attempt: int) -> bool:
        """Determine if request should be retried"""
        # Retry on server errors (5xx) and rate limiting (429)
        retry_codes = [429, 500, 502, 503, 504]
        return status_code in retry_codes and attempt < self.max_retries
    
    def _calculate_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff delay"""
        return self.retry_delay * (2 ** attempt)
    
    def request(
        self,
        method: Literal['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> requests.Response:
        """
        Make HTTP request with retry logic
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request body data
            params: URL query parameters
            headers: Additional headers
            **kwargs: Additional arguments for requests
        
        Returns:
            Response object
        
        Raises:
            requests.RequestException: On request failure
        """
        url = self._build_url(endpoint)
        
        # Merge additional headers
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)
        
        attempt = 0
        last_exception = None
        
        while attempt < self.max_retries:
            try:
                logger.debug(f"Request attempt {attempt + 1}/{self.max_retries}: {method} {url}")
                
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=request_headers,
                    timeout=self.timeout,
                    **kwargs
                )
                
                # Check if we should retry
                if self._should_retry(response.status_code, attempt):
                    attempt += 1
                    backoff = self._calculate_backoff(attempt)
                    logger.warning(
                        f"Request failed with status {response.status_code}. "
                        f"Retrying in {backoff}s..."
                    )
                    time.sleep(backoff)
                    continue
                
                # Raise for bad status codes
                response.raise_for_status()
                
                logger.info(f"Request successful: {method} {url}")
                return response
                
            except requests.RequestException as e:
                last_exception = e
                attempt += 1
                
                if attempt < self.max_retries:
                    backoff = self._calculate_backoff(attempt)
                    logger.warning(f"Request failed: {e}. Retrying in {backoff}s...")
                    time.sleep(backoff)
                else:
                    logger.error(f"Request failed after {self.max_retries} attempts: {e}")
                    raise
        
        # If we get here, all retries failed
        if last_exception:
            raise last_exception
        
        raise requests.RequestException(f"Request failed after {self.max_retries} attempts")
    
    def get(self, endpoint: str, params: Optional[Dict] = None, **kwargs) -> requests.Response:
        """Make GET request"""
        return self.request('GET', endpoint, params=params, **kwargs)
    
    def post(self, endpoint: str, data: Optional[Dict] = None, **kwargs) -> requests.Response:
        """Make POST request"""
        return self.request('POST', endpoint, data=data, **kwargs)
    
    def put(self, endpoint: str, data: Optional[Dict] = None, **kwargs) -> requests.Response:
        """Make PUT request"""
        return self.request('PUT', endpoint, data=data, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """Make DELETE request"""
        return self.request('DELETE', endpoint, **kwargs)
    
    def patch(self, endpoint: str, data: Optional[Dict] = None, **kwargs) -> requests.Response:
        """Make PATCH request"""
        return self.request('PATCH', endpoint, data=data, **kwargs)
    
    def close(self):
        """Close the session"""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class CachedHTTPClient(HTTPClient):
    """
    HTTP client with response caching
    """
    
    def __init__(self, *args, cache_ttl: int = 300, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_ttl = cache_ttl  # Cache TTL in seconds
        self.cache: Dict[str, Dict[str, Any]] = {}
    
    def _get_cache_key(self, method: str, url: str, params: Optional[Dict] = None) -> str:
        """Generate cache key"""
        key = f"{method}:{url}"
        if params:
            key += f":{json.dumps(params, sort_keys=True)}"
        return key
    
    def _get_from_cache(self, cache_key: str) -> Optional[requests.Response]:
        """Get response from cache if valid"""
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            expires_at = cached['expires_at']
            
            if datetime.now() < expires_at:
                logger.debug(f"Cache hit: {cache_key}")
                return cached['response']
            else:
                # Cache expired
                logger.debug(f"Cache expired: {cache_key}")
                del self.cache[cache_key]
        
        return None
    
    def _save_to_cache(self, cache_key: str, response: requests.Response) -> None:
        """Save response to cache"""
        self.cache[cache_key] = {
            'response': response,
            'expires_at': datetime.now() + timedelta(seconds=self.cache_ttl)
        }
        logger.debug(f"Cached response: {cache_key}")
    
    def get(self, endpoint: str, params: Optional[Dict] = None, use_cache: bool = True, **kwargs) -> requests.Response:
        """Make GET request with caching"""
        url = self._build_url(endpoint)
        cache_key = self._get_cache_key('GET', url, params)
        
        # Check cache
        if use_cache:
            cached_response = self._get_from_cache(cache_key)
            if cached_response:
                return cached_response
        
        # Make request
        response = super().get(endpoint, params=params, **kwargs)
        
        # Cache successful responses
        if response.status_code == 200 and use_cache:
            self._save_to_cache(cache_key, response)
        
        return response
    
    def clear_cache(self) -> None:
        """Clear all cached responses"""
        self.cache.clear()
        logger.info("Cache cleared")


# Export classes
__all__ = ['HTTPClient', 'CachedHTTPClient']