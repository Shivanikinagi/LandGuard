"""
FastAPI middleware for security, logging, and rate limiting.
"""

import time
import uuid
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from core.security.audit_logger import AuditLogger, SecurityEvent, SecurityEventType


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all API requests and responses."""
    
    def __init__(self, app, audit_logger: AuditLogger):
        super().__init__(app)
        self.audit_logger = audit_logger
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Record start time
        start_time = time.time()
        
        # Get client info
        client_ip = request.client.host if request.client else "unknown"
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Add custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            # Add rate limit headers if available
            if hasattr(request.state, 'rate_limit_info'):
                limits = request.state.rate_limit_info
                if 'ip' in limits:
                    response.headers["X-RateLimit-Limit"] = str(limits['ip']['limit'])
                    response.headers["X-RateLimit-Remaining"] = str(limits['ip']['remaining'])
                    response.headers["X-RateLimit-Reset"] = str(limits['ip']['window'])
            
            # Log successful request
            user_id = None
            if hasattr(request.state, 'user'):
                user_id = request.state.user.get('user_id', 'unknown')
            
            self.audit_logger.log_data_access(
                user_id=user_id or 'anonymous',
                ip_address=client_ip,
                resource=request.url.path,
                action=request.method,
                details={
                    'request_id': request_id,
                    'status_code': response.status_code,
                    'process_time': process_time
                }
            )
            
            return response
        
        except Exception as e:
            # Log error
            self.audit_logger.log_suspicious_activity(
                user_id=None,
                ip_address=client_ip,
                activity_type='request_error',
                details={
                    'request_id': request_id,
                    'path': request.url.path,
                    'method': request.method,
                    'error': str(e)
                }
            )
            
            # Re-raise to let FastAPI handle it
            raise


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Global error handling middleware."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        
        except Exception as e:
            # Return JSON error response
            return JSONResponse(
                status_code=500,
                content={
                    "error": "internal_server_error",
                    "message": "An unexpected error occurred",
                    "request_id": getattr(request.state, 'request_id', 'unknown')
                }
            )