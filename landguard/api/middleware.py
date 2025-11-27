"""
API Middleware
CORS, logging, error handling, and security middleware
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
import logging
import time
import traceback

# Logger
logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging all requests"""
    
    async def dispatch(self, request: Request, call_next):
        """Log request details"""
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response: {request.method} {request.url.path} "
                f"Status: {response.status_code} "
                f"Time: {process_time:.3f}s"
            )
            
            # Add custom headers
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            logger.error(f"Request failed: {request.method} {request.url.path} Error: {str(e)}")
            logger.error(traceback.format_exc())
            raise


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware for handling errors globally"""
    
    async def dispatch(self, request: Request, call_next):
        """Handle errors and return JSON responses"""
        try:
            response = await call_next(request)
            return response
            
        except Exception as e:
            logger.error(f"Unhandled error: {str(e)}")
            logger.error(traceback.format_exc())
            
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal server error",
                    "message": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers"""
    
    async def dispatch(self, request: Request, call_next):
        """Add security headers to response"""
        response = await call_next(request)
        
        # Check if this is a docs/openapi endpoint
        is_docs = request.url.path in ["/docs", "/redoc", "/openapi.json"]
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Relaxed CSP for documentation pages
        if is_docs:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https:; "
                "font-src 'self' https://cdn.jsdelivr.net;"
            )
        else:
            # Strict CSP for other endpoints
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self'; "
                "img-src 'self' data:; "
                "font-src 'self';"
            )
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware"""
    
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    async def dispatch(self, request: Request, call_next):
        """Rate limit requests by IP"""
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Clean old entries
        self.requests = {
            ip: times for ip, times in self.requests.items()
            if any(t > current_time - self.window_seconds for t in times)
        }
        
        # Check rate limit
        if client_ip in self.requests:
            recent_requests = [
                t for t in self.requests[client_ip]
                if t > current_time - self.window_seconds
            ]
            
            if len(recent_requests) >= self.max_requests:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "Rate limit exceeded",
                        "message": f"Maximum {self.max_requests} requests per {self.window_seconds} seconds"
                    }
                )
            
            self.requests[client_ip] = recent_requests + [current_time]
        else:
            self.requests[client_ip] = [current_time]
        
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(
            self.max_requests - len(self.requests.get(client_ip, []))
        )
        
        return response


def setup_middleware(app: FastAPI):
    """
    Setup all middleware for the FastAPI application
    
    Args:
        app: FastAPI application instance
    """
    
    # CORS Middleware - Allow frontend to access API
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",  # Vite dev server
            "http://localhost:3000",  # Alternative frontend port
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Process-Time", "X-RateLimit-Limit", "X-RateLimit-Remaining"]
    )
    
    # Trusted Host Middleware - Security
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "0.0.0.0", "*.landguard.com"]
    )
    
    # Custom middleware
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)
    app.add_middleware(ErrorHandlerMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    
    logger.info("Middleware setup complete")


# Simple callable functions for decorator-style middleware
async def add_security_headers(request: Request, call_next):
    """
    Add security headers to response (callable function)
    
    Args:
        request: FastAPI Request
        call_next: Next middleware in chain
        
    Returns:
        Response with security headers
    """
    response = await call_next(request)
    
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # Check if this is a docs/openapi endpoint
    is_docs = request.url.path in ["/docs", "/redoc", "/openapi.json"]
    
    if is_docs:
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://cdn.jsdelivr.net;"
        )
    else:
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self'; "
            "img-src 'self' data:; "
            "font-src 'self';"
        )
    
    return response


async def log_requests(request: Request, call_next):
    """
    Log all requests (callable function)
    
    Args:
        request: FastAPI Request
        call_next: Next middleware in chain
        
    Returns:
        Response with process time header
    """
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response: {request.method} {request.url.path} "
            f"Status: {response.status_code} "
            f"Time: {process_time:.3f}s"
        )
        
        # Add custom header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except Exception as e:
        logger.error(f"Request failed: {request.method} {request.url.path} Error: {str(e)}")
        raise


def add_cors_headers(response):
    """
    Add CORS headers to a response manually
    
    Args:
        response: Response object
        
    Returns:
        Response with CORS headers
    """
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


def log_request(request: Request):
    """
    Log request details
    
    Args:
        request: FastAPI Request object
    """
    logger.info(
        f"Request: {request.method} {request.url.path} "
        f"Client: {request.client.host} "
        f"User-Agent: {request.headers.get('user-agent', 'Unknown')}"
    )


def log_response(request: Request, response, process_time: float):
    """
    Log response details
    
    Args:
        request: FastAPI Request object
        response: Response object
        process_time: Time taken to process request
    """
    logger.info(
        f"Response: {request.method} {request.url.path} "
        f"Status: {response.status_code} "
        f"Time: {process_time:.3f}s"
    )


class RequestValidator(BaseHTTPMiddleware):
    """Middleware for validating requests"""
    
    async def dispatch(self, request: Request, call_next):
        """Validate request before processing"""
        
        # Validate content type for POST/PUT requests
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            
            if not content_type:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "error": "Content-Type header required",
                        "message": "POST/PUT/PATCH requests must include Content-Type header"
                    }
                )
        
        response = await call_next(request)
        return response


class CompressionMiddleware(BaseHTTPMiddleware):
    """Middleware for response compression"""
    
    async def dispatch(self, request: Request, call_next):
        """Compress response if client accepts it"""
        response = await call_next(request)
        
        # Check if client accepts gzip
        accept_encoding = request.headers.get("accept-encoding", "")
        
        if "gzip" in accept_encoding.lower():
            response.headers["Content-Encoding"] = "gzip"
        
        return response


def setup_production_middleware(app: FastAPI):
    """
    Setup middleware for production environment
    More strict security and logging
    
    Args:
        app: FastAPI application instance
    """
    
    # CORS - More restrictive in production
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://landguard.com",
            "https://www.landguard.com",
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Content-Type", "Authorization"],
    )
    
    # Trusted hosts - Only production domains
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["landguard.com", "www.landguard.com", "api.landguard.com"]
    )
    
    # Custom middleware
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RateLimitMiddleware, max_requests=50, window_seconds=60)
    app.add_middleware(RequestValidator)
    app.add_middleware(CompressionMiddleware)
    app.add_middleware(ErrorHandlerMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    
    logger.info("Production middleware setup complete")


def setup_development_middleware(app: FastAPI):
    """
    Setup middleware for development environment
    More permissive, with detailed logging
    
    Args:
        app: FastAPI application instance
    """
    
    # CORS - Very permissive in development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Minimal security in development
    app.add_middleware(ErrorHandlerMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    
    logger.info("Development middleware setup complete")