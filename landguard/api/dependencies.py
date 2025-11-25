"""
FastAPI dependencies for authentication and authorization.
"""

from typing import Optional, Dict, Any
from fastapi import Header, HTTPException, status, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from core.security.auth import AuthManager, UserRole, Permission
from core.security.rate_limiter import MultiTierRateLimiter, RateLimitExceeded
from core.security.audit_logger import AuditLogger, SecurityEventType

# Global instances
auth_manager = AuthManager()
rate_limiter = MultiTierRateLimiter()
audit_logger = AuditLogger(log_to_console=True)

security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    authorization: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_api_key: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """
    Get current authenticated user.
    Supports both API key and JWT authentication.
    
    Args:
        request: FastAPI request
        authorization: Bearer token from Authorization header
        x_api_key: API key from X-API-Key header
        
    Returns:
        User information dictionary
        
    Raises:
        HTTPException: If authentication fails
    """
    client_ip = request.client.host if request.client else "unknown"
    
    # Try API key authentication first
    if x_api_key:
        is_valid, user_info = auth_manager.authenticate(x_api_key, 'api_key')
        
        if is_valid:
            audit_logger.log_authentication(
                user_id=user_info.get('role', 'unknown').value if hasattr(user_info.get('role'), 'value') else str(user_info.get('role', 'unknown')),
                ip_address=client_ip,
                success=True,
                auth_method='api_key'
            )
            return user_info
        
        audit_logger.log_authentication(
            user_id='unknown',
            ip_address=client_ip,
            success=False,
            auth_method='api_key'
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # Try JWT authentication
    if authorization:
        token = authorization.credentials
        is_valid, user_info = auth_manager.authenticate(token, 'jwt')
        
        if is_valid:
            audit_logger.log_authentication(
                user_id=user_info.get('user_id', 'unknown'),
                ip_address=client_ip,
                success=True,
                auth_method='jwt'
            )
            return user_info
        
        audit_logger.log_authentication(
            user_id='unknown',
            ip_address=client_ip,
            success=False,
            auth_method='jwt'
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # No authentication provided
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer"}
    )


async def require_permission(
    permission: Permission,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Dependency to require specific permission.
    
    Args:
        permission: Required permission
        user: User information from get_current_user
        
    Raises:
        HTTPException: If user doesn't have permission
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    role = user.get('role')
    if not role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User role not found"
        )
    
    has_permission, error = auth_manager.require_permission(user, permission)
    
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error or "Permission denied"
        )


async def check_rate_limit(request: Request):
    """
    Check rate limits for the request.
    
    Args:
        request: FastAPI request
        
    Raises:
        HTTPException: If rate limit exceeded
    """
    client_ip = request.client.host if request.client else "unknown"
    endpoint = request.url.path
    
    # Extract user_id if available
    user_id = None
    if hasattr(request.state, 'user'):
        user_id = request.state.user.get('user_id')
    
    # Check rate limit
    is_allowed, error_msg = rate_limiter.check_request(
        ip_address=client_ip,
        user_id=user_id,
        endpoint=endpoint.split('/')[-1] if endpoint else None
    )
    
    if not is_allowed:
        # Log rate limit exceeded
        audit_logger.log_rate_limit_exceeded(
            identifier=user_id or client_ip,
            ip_address=client_ip,
            endpoint=endpoint
        )
        
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=error_msg,
            headers={"Retry-After": "60"}
        )
    
    # Add rate limit info to response headers
    limits_info = rate_limiter.get_limits_info(
        ip_address=client_ip,
        user_id=user_id,
        endpoint=endpoint.split('/')[-1] if endpoint else None
    )
    
    # Store in request state for use in response
    request.state.rate_limit_info = limits_info


def get_admin_user(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Dependency that requires admin role.
    
    Args:
        user: User information
        
    Returns:
        User information if admin
        
    Raises:
        HTTPException: If user is not admin
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    if user.get('role') != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return user


def get_analyst_user(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Dependency that requires analyst role or higher.
    
    Args:
        user: User information
        
    Returns:
        User information if analyst or admin
        
    Raises:
        HTTPException: If user is not analyst or admin
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    role = user.get('role')
    if role not in [UserRole.ANALYST, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Analyst access required"
        )
    
    return user